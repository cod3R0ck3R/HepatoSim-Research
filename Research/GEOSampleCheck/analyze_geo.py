#!/usr/bin/env python3
"""Bounded, sample-level GEO matrix audit; no cell-level efficacy inference."""
import argparse
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import signal
import resource
import sys
import tarfile
import time
import numpy as np


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def write_new(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


def sample_hash(sample):
    return hashlib.sha256(json.dumps(sample, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def read_checkpoint(path, binding):
    old = json.loads(Path(path).read_text())
    if old['binding'] != binding or old['sample_sha256'] != sample_hash(old['sample']):
        raise ValueError('Stale or damaged checkpoint')
    return old['sample']


def coordinates(stream, expected=None, chunk=100000):
    if stream.readline().strip() != b'%%MatrixMarket matrix coordinate integer general':
        raise ValueError('Unsupported MatrixMarket header')
    line = stream.readline()
    while line.startswith(b'%'):
        line = stream.readline()
    dims = tuple(map(int, line.split()))
    if len(dims) != 3 or min(dims) <= 0 or (expected and dims != expected):
        raise ValueError('Invalid dimensions')
    genes, cells, nnz = dims
    if genes > 100000 or cells > 100000 or nnz > 100000000:
        raise ValueError('Exceeds bounded parser capacity')
    seen, previous, total = 0, -1, 0
    while True:
        cpu_start, wall_start = time.process_time(), time.monotonic()
        lines = list(itertools.islice(stream, chunk))
        if not lines:
            break
        data = np.fromstring(b''.join(lines).decode('ascii'), dtype=np.int64, sep=' ')
        if data.size != 3 * len(lines):
            raise ValueError('Malformed coordinate rows')
        data = data.reshape(-1, 3)
        r, c, v = data.T
        if np.any((r < 1) | (r > genes) | (c < 1) | (c > cells) | (v <= 0) | (v > 2**31-1)):
            raise ValueError('Coordinate/count out of bounds')
        keys = (c-1)*genes + r-1
        if keys[0] <= previous or np.any(np.diff(keys) <= 0):
            raise ValueError('Duplicate or unsorted coordinates; this parser requires column-major order')
        previous = int(keys[-1]); seen += len(data); total += int(v.sum())
        if seen > nnz or total > 2**53:
            raise ValueError('Invalid nnz or unsafe exact-count range')
        yield dims, r-1, c-1, v
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak_bytes = peak if sys.platform == 'darwin' else peak * 1024
        if peak_bytes > 512 * 1024**2:
            raise MemoryError('Bounded scan exceeded 512 MiB observed peak RSS')
        # Enforce low average CPU demand across parsing AND caller aggregation.
        pause = (time.process_time()-cpu_start)/0.20 - (time.monotonic()-wall_start)
        if pause > 0:
            time.sleep(pause)
    if seen != nnz:
        raise ValueError('Truncated matrix')


def sum_counts(index, values, size):
    # All integers remain exactly representable under the checked 2**53 total bound.
    return np.bincount(index, weights=values, minlength=size).astype(np.int64)


def audit_sample(tar, sample, group, targets, qc):
    def member(suffix):
        hits = [x for x in tar.getmembers() if x.name.startswith(sample+'_') and x.name.endswith(suffix)]
        if len(hits) != 1 or not hits[0].isfile():
            raise ValueError('Missing/duplicate/nonfile sample member')
        return hits[0]
    def raw(suffix):
        return gzip.decompress(tar.extractfile(member(suffix)).read())
    fb, bb = raw('features.tsv.gz'), raw('barcodes.tsv.gz')
    features = [x.split('\t') for x in fb.decode().splitlines()]
    barcodes = bb.decode().splitlines()
    if not features or any(len(x) != 3 or x[2] != 'Gene Expression' for x in features):
        raise ValueError('Unsupported feature schema')
    if len(set(x[0] for x in features)) != len(features) or len(set(barcodes)) != len(barcodes):
        raise ValueError('Duplicate features/barcodes')
    indices = []
    for target in targets:
        hits = [i for i, x in enumerate(features) if x[1] == target]
        if len(hits) != 1:
            raise ValueError('Missing/ambiguous target '+target)
        indices.append(hits[0])
    ng, nc = len(features), len(barcodes)
    mt = np.array([x[1].startswith(qc['mitochondrial_symbol_prefix']) for x in features])
    detections = np.zeros(ng, dtype=np.int64)
    raw_gene = np.zeros(ng, dtype=np.int64)
    raw_cell = np.zeros(nc, dtype=np.int64)
    matrix = member('matrix.mtx.gz')
    dims = None
    with gzip.GzipFile(fileobj=tar.extractfile(matrix)) as f:
        for dims, r, c, v in coordinates(f):
            if dims[:2] != (ng, nc):
                raise ValueError('Feature/barcode dimension mismatch')
            detections += np.bincount(r, minlength=ng)
            raw_gene += sum_counts(r, v, ng)
            raw_cell += sum_counts(c, v, nc)
    keep_gene = detections >= qc['gene_min_cells']
    counts = np.zeros(nc, dtype=np.int64); detected = counts.copy(); mito = counts.copy()
    target_cells = np.zeros((len(targets), nc), dtype=np.int64)
    with gzip.GzipFile(fileobj=tar.extractfile(matrix)) as f:
        for _, r, c, v in coordinates(f, dims):
            use = keep_gene[r]; r, c, v = r[use], c[use], v[use]
            counts += sum_counts(c, v, nc); detected += np.bincount(c, minlength=nc)
            mito += sum_counts(c[mt[r]], v[mt[r]], nc)
            for k, index in enumerate(indices):
                m = r == index; target_cells[k] += sum_counts(c[m], v[m], nc)
    pct = np.divide(100.0*mito, counts, out=np.zeros(nc), where=counts != 0)
    keep = ((detected > qc['features_strict_min']) & (detected < qc['features_strict_max']) &
            (counts < qc['counts_strict_max']) & (pct < qc['mitochondrial_percent_strict_max']))
    if not np.any(keep) or int(counts[keep].sum()) <= 0:
        raise ValueError('No cells/counts survive QC')
    def distribution(a):
        return {k: float(v) for k, v in zip(('min','q25','median','q75','max'), np.percentile(a, [0,25,50,75,100]))}
    return {'sample':sample, 'group':group, 'matrix_member':matrix.name, 'dimensions':list(dims),
            'feature_sha256':hashlib.sha256(fb).hexdigest(), 'barcode_sha256':hashlib.sha256(bb).hexdigest(),
            'unique_coordinates':True, 'raw_barcodes':nc, 'retained_barcodes':int(keep.sum()),
            'genes_retained':int(keep_gene.sum()), 'mitochondrial_features':int(mt.sum()),
            'raw_cell_counts':distribution(raw_cell), 'qc_input_detected_genes':distribution(detected),
            'qc_input_mitochondrial_percent':distribution(pct),
            'exclusions_overlapping':{'low_features':int((detected <= qc['features_strict_min']).sum()),
              'high_features':int((detected >= qc['features_strict_max']).sum()),
              'high_counts':int((counts >= qc['counts_strict_max']).sum()),
              'high_mito':int((pct >= qc['mitochondrial_percent_strict_max']).sum())},
            'raw':{'total':int(raw_gene.sum()),'targets':dict(zip(targets, map(int,raw_gene[indices])))},
            'qc':{'total':int(counts[keep].sum()),'targets':dict(zip(targets,map(int,target_cells[:,keep].sum(axis=1))))}}


def contrast(a, b):
    effect = float(np.mean(a)-np.mean(b)); pooled = np.array([*a,*b])
    stats = []
    for select in itertools.combinations(range(6),3):
        mask = np.zeros(6, dtype=bool); mask[list(select)] = True
        stats.append(float(pooled[mask].mean()-pooled[~mask].mean()))
    p = sum(abs(x) >= abs(effect)-1e-12 for x in stats)/len(stats)
    loo = [float(np.mean(np.delete(a,i))-np.mean(np.delete(b,j))) for i in range(3) for j in range(3)]
    return {'mean_log2cpm_difference':effect,'exact_permutation_p':p,'loo_min':min(loo),'loo_max':max(loo),
            'loo_direction_stable':bool((min(loo)>0 and effect>0) or (max(loo)<0 and effect<0))}


def bh(values):
    order = sorted(range(len(values)), key=lambda i:values[i]); out = [0.0]*len(values); last = 1.0
    for rank in range(len(values),0,-1):
        i=order[rank-1]; last=min(last, values[i]*len(values)/rank); out[i]=last
    return out


def summarize(spec, samples):
    expected = {s:g for g,ss in spec['groups'].items() for s in ss}
    if len(samples) != 9 or {s['sample']:s['group'] for s in samples} != expected:
        raise ValueError('Nine correctly assigned, distinct libraries required')
    if len({x['feature_sha256'] for x in samples}) != 1:
        raise ValueError('Feature reference mismatch')
    results = {}
    for branch in ['raw','qc']:
        rows=[]
        for target in spec['targets']:
            values={s['sample']:math.log2(1+1e6*s[branch]['targets'][target]/s[branch]['total']) for s in samples}
            for first,second in spec['contrasts']:
                row={'gene':target,'contrast':first+'-'+second,'sample_log2cpm':values,
                     **contrast([values[s] for s in spec['groups'][first]],[values[s] for s in spec['groups'][second]])}
                rows.append(row)
        for row,q in zip(rows,bh([r['exact_permutation_p'] for r in rows])): row['bh_q']=q
        results[branch]=rows
    for raw,qc in zip(results['raw'],results['qc']):
        qc['direction_stable_across_qc_and_loo']=bool(raw['loo_direction_stable'] and qc['loo_direction_stable'] and raw['mean_log2cpm_difference']*qc['mean_log2cpm_difference']>0)
    return {'schema_version':1,'scope':spec['scope'],'samples':samples,'contrasts':results,
            'totals':{'raw_barcodes':sum(s['raw_barcodes'] for s in samples),'retained_barcodes':sum(s['retained_barcodes'] for s in samples)},
            'independent_validation':False,'drug_effect_estimated':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,required=True); p.add_argument('--archive',type=Path)
    p.add_argument('--checkpoints',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    p.add_argument('--replay',action='store_true'); args=p.parse_args()
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Budget expired; checkpoints retained')))
    signal.alarm(600); spec=json.loads(args.spec.read_text()); binding={'spec_sha256':sha(args.spec),'code_sha256':sha(__file__),'archive_sha256':spec['archive_sha256']}
    args.checkpoints.mkdir(parents=True,exist_ok=True); start=time.monotonic(); cpu_start=time.process_time(); samples=[]
    if not args.replay and (args.archive is None or sha(args.archive)!=spec['archive_sha256']): raise ValueError('Archive hash mismatch')
    archive=tarfile.open(args.archive) if not args.replay else None
    if archive:
        found = [x.name.split('_')[0] for x in archive.getmembers() if x.name.endswith('matrix.mtx.gz')]
        expected = [s for group in spec['groups'].values() for s in group]
        if sorted(found) != sorted(expected): raise ValueError('Archive must contain exactly the nine specified matrices')
    try:
        for group,ids in spec['groups'].items():
            for sample in ids:
                file=args.checkpoints/(sample+'.json')
                if file.exists():
                    row=read_checkpoint(file,binding)
                else:
                    if args.replay: raise ValueError('Missing replay checkpoint')
                    row=audit_sample(archive,sample,group,spec['targets'],spec['qc'])
                    write_new(file,{'binding':binding,'sample':row,'sample_sha256':sample_hash(row)})
                samples.append(row); print(sample,row['raw_barcodes'],row['retained_barcodes'],flush=True)
        result=summarize(spec,samples); result['binding']=binding
        write_new(args.output,result); print(json.dumps({'seconds':round(time.monotonic()-start,3),'cpu_seconds':round(time.process_time()-cpu_start,3),'observed_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if sys.platform=='darwin' else resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'result_sha256':sha(args.output),'totals':result['totals']}))
    finally:
        if archive: archive.close()


if __name__=='__main__': main()
