"""Donor/cell-type pseudobulk with exact author-barcode joins and bounded sparse scans."""
import argparse
import csv
import gzip
import json
import math
from pathlib import Path
import re
import resource
import signal
import sys
import time
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'GEOSampleCheck'))
from analyze_geo import coordinates, sum_counts, contrast, bh, sha, write_new, read_checkpoint, sample_hash


def annotations(path, samples):
    result = {s['donor']: {} for s in samples}
    by_donor = {s['donor']: s for s in samples}
    with Path(path).open() as stream:
        for row in csv.DictReader(stream):
            donor = row['donor_id']; sample = by_donor[donor]
            match = re.fullmatch(r'Liver\.(\d+)_([ACGT]+)\.(\d+)-[01]', row['index'])
            if not match or match[1] != sample['liver'] or row['sample_id'] != donor or row['Condition'] != sample['condition']:
                raise ValueError('Annotation/sample identity mismatch')
            barcode = match[2] + '-' + match[3]
            cell_type = row['CellType_healthy' if sample['condition'] == 'Normal' else 'CellType_injured']
            if not cell_type or barcode in result[donor]:
                raise ValueError('Missing cell label or duplicate retained barcode')
            result[donor][barcode] = cell_type
    if any(not x for x in result.values()):
        raise ValueError('Empty donor annotation')
    return result


def join_barcodes(stream, labels):
    positions, types, seen = [], [], set()
    count = 0
    for count, line in enumerate(stream, 1):
        barcode = line.strip()
        if barcode in labels:
            if barcode in seen:
                raise ValueError('Duplicate matched raw barcode')
            seen.add(barcode); positions.append(count-1); types.append(labels[barcode])
    if seen != set(labels):
        raise ValueError('Not all annotated nuclei matched raw barcodes')
    if not 1 <= count <= 10000000:
        raise ValueError('Barcode count exceeds capacity')
    return np.array(positions, dtype=np.int64), np.array(types), count


def aggregate(stream, positions, ng, nc, target_indices):
    totals = np.zeros(len(positions), dtype=np.int64)
    targets = np.zeros((len(target_indices), len(positions)), dtype=np.int64)
    dims = None
    for dims, r, c, v in coordinates(stream, max_cells=nc):
        if dims[:2] != (ng, nc):
            raise ValueError('Feature/barcode matrix dimension mismatch')
        lookup = np.searchsorted(positions, c)
        safe = np.minimum(lookup, len(positions)-1)
        use = (lookup < len(positions)) & (positions[safe] == c)
        r, v, lookup = r[use], v[use], lookup[use]
        totals += sum_counts(lookup, v, len(positions))
        for i, target in enumerate(target_indices):
            mask = r == target
            targets[i] += sum_counts(lookup[mask], v[mask], len(positions))
    if dims is None or np.any(totals <= 0):
        raise ValueError('Empty retained nucleus or matrix')
    return totals, targets, dims


def audit(source, sample, labels, spec):
    prefix = sample['gsm'] + '_6854-' + sample['liver']
    with gzip.open(source / (prefix+'_features.tsv.gz'), 'rt') as f:
        features = [line.rstrip('\n').split('\t') for line in f]
    if any(len(x) != 3 or x[2] != 'Gene Expression' for x in features) or len({x[0] for x in features}) != len(features):
        raise ValueError('Unsupported/duplicate features')
    indices = []
    for target in spec['targets']:
        matches = [i for i, row in enumerate(features) if row[1] == target]
        if len(matches) != 1:
            raise ValueError('Missing or ambiguous target: '+target)
        indices.append(matches[0])
    with gzip.open(source / (prefix+'_barcodes.tsv.gz'), 'rt') as f:
        positions, types, nc = join_barcodes(f, labels)
    with gzip.open(source / (prefix+'_matrix.mtx.gz'), 'rb') as f:
        totals, targets, dims = aggregate(f, positions, len(features), nc, indices)
    rows = []
    for cell_type in sorted(set(types)):
        mask = types == cell_type; total = int(totals[mask].sum()); n = int(mask.sum())
        rows.append({'cell_type':str(cell_type), 'nuclei':n, 'total_umi':total,
                     'eligible':n >= spec['min_nuclei'],
                     'genes':{g:{'umi':int(targets[i,mask].sum()),
                                 'detected_nuclei':int((targets[i,mask]>0).sum()),
                                 'detection_fraction':float((targets[i,mask]>0).mean()),
                                 'log2cpm':math.log2(1+1e6*int(targets[i,mask].sum())/total)}
                              for i,g in enumerate(spec['targets'])}})
    return {**sample, 'dimensions':list(dims), 'matched_nuclei':len(positions),
            'feature_sha256':sha(source/(prefix+'_features.tsv.gz')), 'strata':rows}


def summarize(spec, samples):
    if len(samples) != 6 or {s['donor']:s['condition'] for s in samples} != {s['donor']:s['condition'] for s in spec['samples']}:
        raise ValueError('Six distinct correctly assigned donors required')
    rows=[]
    for item in spec['primary']:
        values = {}
        for sample in samples:
            matches=[r for r in sample['strata'] if r['cell_type']==item['cell_type'] and r['eligible']]
            if len(matches)==1: values[sample['donor']]=matches[0]['genes'][item['gene']]['log2cpm']
        row={**item,'donor_log2cpm':values,'available':len(values)==6}
        if row['available']:
            row.update(contrast([values[s['donor']] for s in samples if s['condition']=='Disease'],
                                [values[s['donor']] for s in samples if s['condition']=='Normal']))
        rows.append(row)
    if all(r['available'] for r in rows):
        for row,q in zip(rows,bh([r['exact_permutation_p'] for r in rows])): row['bh_q']=q
    return {'version':1,'samples':samples,'primary':rows,
            'pair_direction_stable':all(r['available'] and r['mean_log2cpm_difference']>0 and r['loo_min']>0 for r in rows),
            'independent_mechanistic_validation':False,'treatment_effect_estimated':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('spec','manifest','source','checkpoints','output'): p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--replay',action='store_true'); args=p.parse_args()
    spec=json.loads(args.spec.read_text()); manifest=json.loads(args.manifest.read_text())
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Budget exhausted; per-donor checkpoints retained')))
    signal.alarm(spec['budget']['compute_timeout_s'])
    start=time.monotonic(); cpu=time.process_time()
    annotation=args.source/'cell_properties_healthy_diseased_nucseq.csv'
    assert sha(annotation)==spec['annotation_sha256']
    binding={'spec_sha256':sha(args.spec),'manifest_sha256':sha(args.manifest),'code_sha256':sha(__file__),
             'shared_code_sha256':sha(Path(__file__).resolve().parents[1]/'GEOSampleCheck/analyze_geo.py')}
    if not args.replay:
        for f in manifest:
            file=args.source/f['name']
            if file.stat().st_size!=f['size'] or sha(file)!=f['sha256']: raise ValueError('Source hash/size mismatch')
    labels=annotations(annotation,spec['samples']); args.checkpoints.mkdir(parents=True,exist_ok=True); samples=[]
    for sample in spec['samples']:
        checkpoint=args.checkpoints/(sample['donor']+'.json')
        if checkpoint.exists(): row=read_checkpoint(checkpoint,binding)
        else:
            if args.replay: raise ValueError('Missing replay checkpoint')
            row=audit(args.source,sample,labels[sample['donor']],spec)
            write_new(checkpoint,{'binding':binding,'sample':row,'sample_sha256':sample_hash(row)})
        samples.append(row); print(sample['donor'],row['matched_nuclei'],'matched',flush=True)
    result=summarize(spec,samples);result['binding']=binding;write_new(args.output,result)
    print(json.dumps({'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,
                     'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),
                     'result_sha256':sha(args.output)}))


if __name__=='__main__': main()
