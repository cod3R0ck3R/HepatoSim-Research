"""Post hoc common-feature denominator audit; leaves the frozen primary result intact."""
import copy
import gzip
import json
from pathlib import Path
import signal
import re
import sys
import time
import numpy as np
from analyze import annotations, join_barcodes, coordinates, sum_counts, summarize, sha, write_new, read_checkpoint, sample_hash


def normalize_ids(rows):
    for row in rows: row[0]=re.sub(r'\.\d+$','',row[0])
    if len({r[0] for r in rows})!=len(rows): raise ValueError('Ambiguous base gene IDs')
    return rows


def common_totals(stream, positions, allowed, nc):
    total=np.zeros(len(positions),dtype=np.int64)
    for dims,r,c,v in coordinates(stream,max_cells=nc):
        if dims[:2]!=(len(allowed),nc): raise ValueError('Reference dimension mismatch')
        q=np.searchsorted(positions,c); safe=np.minimum(q,len(positions)-1)
        use=(q<len(positions)) & (positions[safe]==c) & allowed[r]
        total+=sum_counts(q[use],v[use],len(positions))
    if np.any(total<=0): raise ValueError('Empty common-feature nucleus')
    return total


def main():
    root=Path(sys.argv[1]); output=Path(sys.argv[2]); replay='--replay' in sys.argv[3:]
    module=Path(__file__).parent; spec=json.loads((module/'specification-v1.json').read_text())
    sensitivity=json.loads((module/'sensitivity-spec-v2.json').read_text())
    original=json.loads((root/'result-v1.json').read_text()); assert sha(root/'result-v1.json')==sensitivity['primary_result_sha256']
    source=root/'sources'; files=json.loads((module/'input-manifest.json').read_text())
    if not replay:
        for f in files: assert sha(source/f['name'])==f['sha256']
    labels=annotations(source/'cell_properties_healthy_diseased_nucseq.csv',spec['samples']); references={}
    for s in spec['samples']:
        prefix=s['gsm']+'_6854-'+s['liver']
        with gzip.open(source/(prefix+'_features.tsv.gz'),'rt') as f: references[s['donor']]=normalize_ids([x.strip().split('\t') for x in f])
    common=set.intersection(*[set(x[0] for x in ref) for ref in references.values()])
    for gene in spec['targets']:
        ids=[{x[0] for x in ref if x[1]==gene} for ref in references.values()]
        if len(ids[0])!=1 or any(x!=ids[0] for x in ids) or not ids[0]<=common: raise ValueError('Target identity differs')
    binding={'primary':sha(root/'result-v1.json'),'spec':sha(module/'sensitivity-spec-v2.json'),'code':sha(__file__),
             'analysis':sha(module/'analyze.py'),'shared':sha(module.parent/'GEOSampleCheck/analyze_geo.py')}
    cp=root/'common-checkpoints';cp.mkdir(exist_ok=True);samples=[];start=time.monotonic()
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Sensitivity budget exhausted')));signal.alarm(900)
    for old in original['samples']:
        checkpoint=cp/(old['donor']+'.json');sample=copy.deepcopy(old)
        if checkpoint.exists(): sample=read_checkpoint(checkpoint,binding)
        else:
            if replay: raise ValueError('Missing common-feature checkpoint')
            prefix=old['gsm']+'_6854-'+old['liver'];ref=references[old['donor']]
            with gzip.open(source/(prefix+'_barcodes.tsv.gz'),'rt') as f: positions,types,nc=join_barcodes(f,labels[old['donor']])
            with gzip.open(source/(prefix+'_matrix.mtx.gz'),'rb') as f: totals=common_totals(f,positions,np.array([x[0] in common for x in ref]),nc)
            for row in sample['strata']:
                total=int(totals[types==row['cell_type']].sum());row['total_umi']=total
                for gene in row['genes'].values(): gene['log2cpm']=float(np.log2(1+1e6*gene['umi']/total))
            write_new(checkpoint,{'binding':binding,'sample':sample,'sample_sha256':sample_hash(sample)})
        samples.append(sample);print(old['donor'],'common-feature denominator',flush=True)
    result=summarize(spec,samples);result.update({'binding':binding,'post_hoc':True,'common_gene_ids':len(common),
      'common_gene_ids_sha256':__import__('hashlib').sha256('\n'.join(sorted(common)).encode()).hexdigest()})
    write_new(output,result);print(json.dumps({'seconds':time.monotonic()-start,'result_sha256':sha(output)}))


if __name__=='__main__': main()
