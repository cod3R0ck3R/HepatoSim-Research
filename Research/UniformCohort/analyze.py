#!/usr/bin/env python3
"""GSE244832: bounded donor x original-cluster audit, without invented cell labels."""
import argparse
import csv
import itertools
import json
import math
from pathlib import Path
import resource
import signal
import sys
import tarfile
import time
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'GEOSampleCheck'))
import analyze_geo as shared


def metadata(directory, spec):
    def column(name):
        with (directory/name).open() as f:
            rows=list(csv.reader(f))
        if any(len(r)!=1 for r in rows): raise ValueError('Expected one-column headerless CSV')
        return [r[0] for r in rows]
    genes, cells = column('hLIVER_genes.csv'), column('hLIVER_cells.csv')
    if len(genes)!=spec['dimensions'][0] or len(cells)!=spec['dimensions'][1]: raise ValueError('Dimension mismatch')
    if len(set(genes))!=len(genes) or len(set(cells))!=len(cells): raise ValueError('Duplicate genes/cells')
    with (directory/'hLIVER_metadata.csv').open() as f: rows=list(csv.DictReader(f))
    if [r[''] for r in rows]!=cells: raise ValueError('Metadata/cell order mismatch')
    donors=list(spec['donors']); clusters=spec['clusters']; keys=[]; expected=[]; features=[]
    for r in rows:
        d=r['orig.ident']; c=int(r['seurat_clusters'])
        if d not in donors or r['condition']!=spec['donors'][d] or c not in clusters: raise ValueError('Invalid donor/condition/cluster')
        keys.append(donors.index(d)*len(clusters)+clusters.index(c))
        expected.append(int(r['nCount_RNA'])); features.append(int(r['nFeature_RNA']))
    targets=spec['targets']+spec['markers']
    if any(genes.count(g)!=1 for g in targets): raise ValueError('Missing/ambiguous gene')
    lookup=np.full(len(genes),-1,dtype=np.int64)
    for i,g in enumerate(targets):lookup[genes.index(g)]=i
    return np.array(keys),np.array(expected),np.array(features),lookup


def aggregate(stream, spec, keys, expected_counts, expected_features, lookup):
    ng,nc,nnz=spec['dimensions']; ns=len(spec['donors'])*len(spec['clusters']); nt=len(spec['targets']+spec['markers'])
    counts=np.zeros(nc,dtype=np.int64); features=counts.copy()
    selected=np.zeros(ns*nt,dtype=np.int64); detected=selected.copy()
    for _,r,c,v in shared.coordinates(stream,expected=(ng,nc,nnz),max_cells=nc,max_nnz=spec['budget']['parser_max_nnz']):
        counts+=shared.sum_counts(c,v,nc); features+=np.bincount(c,minlength=nc)
        hit=lookup[r]>=0; index=keys[c[hit]]*nt+lookup[r[hit]]
        selected+=shared.sum_counts(index,v[hit],ns*nt)
        detected+=np.bincount(index,minlength=ns*nt)
    if not np.array_equal(counts,expected_counts): raise ValueError('Matrix count totals disagree with author nCount_RNA')
    if not np.array_equal(features,expected_features): raise ValueError('Matrix detections disagree with author nFeature_RNA')
    return {'nuclei':np.bincount(keys,minlength=ns).tolist(),
            'total_counts':shared.sum_counts(keys,counts,ns).tolist(),
            'gene_counts':selected.reshape(ns,nt).tolist(),'gene_detected_nuclei':detected.reshape(ns,nt).tolist(),
            'count_oracle_exact':True,'feature_oracle_exact':True,'total_UMI':int(counts.sum())}


def statistics(a,b,rng,boots=5000):
    a=np.asarray(a,dtype=float); b=np.asarray(b,dtype=float)
    if min(len(a),len(b))<2 or not np.all(np.isfinite(np.r_[a,b])): raise ValueError('Invalid donor vectors')
    pool=np.r_[a,b]; effect=float(a.mean()-b.mean()); total=0; extreme=0
    # Enumerate smaller group: complements give the same two-sided null distribution.
    n=min(len(a),len(b))
    for chosen in itertools.combinations(range(len(pool)),n):
        mask=np.zeros(len(pool),dtype=bool);mask[list(chosen)]=True
        s=float(pool[mask].mean()-pool[~mask].mean());total+=1;extreme+=abs(s)>=abs(effect)-1e-12
    loo=[float(np.delete(a,i).mean()-np.delete(b,j).mean()) for i in range(len(a)) for j in range(len(b))]
    boot=a[rng.integers(len(a),size=(boots,len(a)))].mean(axis=1)-b[rng.integers(len(b),size=(boots,len(b)))].mean(axis=1)
    return {'mean_log2cpm_difference':effect,'exact_permutation_p':extreme/total,'permutations':total,
            'bootstrap95':np.percentile(boot,[2.5,97.5]).tolist(),'loo_min':min(loo),'loo_max':max(loo),
            'loo_sign_stable':bool(min(loo)>0 or max(loo)<0)}


def summarize(spec, data):
    donors=list(spec['donors']); clusters=spec['clusters']; genes=spec['targets']+spec['markers']; rows=[]; tests=[]
    if not set(spec['contrast']).issubset(set(spec['donors'].values())): raise ValueError('Contrast labels absent from source metadata')
    rng=np.random.Generator(np.random.PCG64(spec['statistics']['seed']))
    for i,d in enumerate(donors):
        for j,c in enumerate(clusters):
            k=i*len(clusters)+j;n=data['nuclei'][k];tot=data['total_counts'][k]
            if n and not tot:raise ValueError('Nonempty compartment has no counts')
            rows.append({'donor':d,'condition':spec['donors'][d],'cluster':c,'nuclei':n,'total_UMI':tot,
                'genes':{g:{'UMI':data['gene_counts'][k][t],'detected_nuclei':data['gene_detected_nuclei'][k][t],
                  'log2cpm':math.log2(1+1e6*data['gene_counts'][k][t]/tot) if tot else None} for t,g in enumerate(genes)}})
    for c in clusters:
        groups={g:[r for r in rows if r['cluster']==c and r['condition']==g and r['nuclei']>=spec['min_nuclei']] for g in spec['contrast']}
        for gene in spec['targets']:
            a,b=[groups[g] for g in spec['contrast']]
            t={'cluster':c,'gene':gene,'disease_donors':[r['donor'] for r in a],'control_donors':[r['donor'] for r in b]}
            if min(len(a),len(b))>=spec['min_donors_per_group']:
                t.update(statistics([r['genes'][gene]['log2cpm'] for r in a],[r['genes'][gene]['log2cpm'] for r in b],rng))
                t['status']='exploratory_tested'
            else:t.update(status='insufficient_donors',exact_permutation_p=1.0)
            tests.append(t)
    for t,q in zip(tests,shared.bh([t['exact_permutation_p'] for t in tests])):t['bh_q_36']=q
    return {'schema_version':1,'accession':spec['accession'],'scope':spec['purpose'],'dimensions':spec['dimensions'],
        'donor_n':len(donors),'group_donors':{g:sum(x==g for x in spec['donors'].values()) for g in sorted(set(spec['donors'].values()))},
        'audit':{k:data[k] for k in ['count_oracle_exact','feature_oracle_exact','total_UMI']},
        'donor_cluster_values':rows,'exploratory_tests':tests,'compartment_annotation_verified':False,
        'independent_biological_validation':False,'drug_effect_estimated':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',type=Path,required=True)
    p.add_argument('--data-dir',type=Path);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--replay',action='store_true');args=p.parse_args()
    spec=json.loads(args.spec.read_text());signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('900-second budget expired')));signal.alarm(spec['budget']['wall_seconds'])
    binding={'spec_sha256':shared.sha(args.spec),'code_sha256':shared.sha(__file__),'parser_sha256':shared.sha(shared.__file__),
             'numpy':np.__version__,'source_hashes':{k:v['sha256'] for k,v in spec['files'].items()}}
    start=time.monotonic();cpu=time.process_time()
    if args.checkpoint.exists():data=shared.read_checkpoint(args.checkpoint,binding)
    else:
        if args.replay:raise ValueError('Missing checkpoint')
        if not args.data_dir:raise ValueError('Missing source directory')
        for name,receipt in spec['files'].items():
            if shared.sha(args.data_dir/name)!=receipt['sha256']:raise ValueError('Source hash mismatch: '+name)
        keys,expected,features,lookup=metadata(args.data_dir,spec)
        with tarfile.open(args.data_dir/'processed.tar.gz','r|gz') as archive:
            data=None
            for member in archive:
                if member.name==spec['matrix_member']:
                    if data is not None or not member.isfile():raise ValueError('Duplicate/nonfile matrix')
                    data=aggregate(archive.extractfile(member),spec,keys,expected,features,lookup)
            if data is None:raise ValueError('Missing matrix')
        shared.write_new(args.checkpoint,{'binding':binding,'sample':data,'sample_sha256':shared.sample_hash(data)})
    result=summarize(spec,data);result['binding']=binding;shared.write_new(args.output,result)
    print(json.dumps({'wall_seconds':round(time.monotonic()-start,3),'cpu_seconds':round(time.process_time()-cpu,3),
      'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if sys.platform=='darwin' else resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
      'result_sha256':shared.sha(args.output),'tested':sum(t['status']=='exploratory_tested' for t in result['exploratory_tests'])}))


if __name__=='__main__':main()
