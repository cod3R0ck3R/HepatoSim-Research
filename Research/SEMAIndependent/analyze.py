#!/usr/bin/env python3
"""Prespecified external-cohort RNA association; no treatment or causal inference."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import resource
import tarfile
import time
import xml.etree.ElementTree as ET

import numpy as np

NS = {'m': 'http://www.ncbi.nlm.nih.gov/geo/info/MINiML'}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def save(path, obj):
    with open(path, 'x') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')


def metadata(path):
    with tarfile.open(path) as t:
        ms = [m for m in t.getmembers() if m.name.endswith('.xml') and m.isfile()]
        if len(ms) != 1:
            raise ValueError('Expected one MINiML XML')
        root = ET.fromstring(t.extractfile(ms[0]).read())
    rows = []
    for s in root.findall('m:Sample', NS):
        c = {x.attrib['tag']: x.text.strip() for x in s.findall('.//m:Characteristics', NS)}
        links = s.findall('m:Supplementary-Data', NS)
        bio = [x.attrib['target'] for x in s.findall('m:Relation', NS) if x.attrib.get('type') == 'BioSample']
        if len(links) != 1 or len(bio) != 1:
            raise ValueError('Ambiguous counts/BioSample')
        rows.append({'id': s.attrib['iid'], 'title': s.findtext('m:Title', namespaces=NS),
                     'bio': bio[0], 'file': links[0].text.strip().split('/')[-1],
                     'disease': c['disease'], 'stage': int(c['fibrosis stage'])})
    for key in ('id', 'title', 'bio', 'file'):
        if len({r[key] for r in rows}) != len(rows):
            raise ValueError('Duplicate ' + key)
    if len(rows) != 216 or any(r['stage'] not in range(5) for r in rows):
        raise ValueError('Unexpected cohort metadata')
    return sorted(rows, key=lambda r: r['id'])


def counts(lines, genes):
    values, seen, total = {}, set(), 0
    for line in lines:
        fields = line.strip().split('\t')
        if len(fields) != 2 or not fields[1].isdigit():
            raise ValueError('Invalid count row')
        gene, raw = fields
        value = int(raw)
        if gene in seen:
            raise ValueError('Duplicate gene')
        seen.add(gene)
        if gene.startswith('__'):
            continue
        if not gene.startswith('ENSG'):
            raise ValueError('Unexpected identifier')
        total += value
        if gene in genes:
            values[gene] = value
    if total <= 0 or total >= 2**53 or set(values) != set(genes):
        raise ValueError('Missing target or invalid total')
    return total, values, len([g for g in seen if not g.startswith('__')])


def bh(p):
    p = np.asarray(p)
    order = np.argsort(p)
    q = np.empty(len(p))
    q[order] = np.minimum(1, np.minimum.accumulate((p[order] * len(p) / np.arange(1, len(p)+1))[::-1])[::-1])
    return q


def ranks(a):
    a = np.asarray(a)
    out = np.empty(len(a), float)
    order = np.argsort(a, kind='stable')
    i = 0
    while i < len(a):
        j = i + 1
        while j < len(a) and a[order[j]] == a[order[i]]:
            j += 1
        out[order[i:j]] = (i + 1 + j) / 2
        i = j
    return out


def statistics(a, b, rng, permutations=9999, bootstraps=2000):
    effect = float(np.mean(a)-np.mean(b))
    pooled = np.concatenate([a,b])
    extreme = 0
    for _ in range(permutations):
        x = rng.permutation(pooled)
        extreme += abs(x[:len(a)].mean()-x[len(a):].mean()) >= abs(effect)-1e-12
    boot = np.array([rng.choice(a,len(a)).mean()-rng.choice(b,len(b)).mean() for _ in range(bootstraps)])
    loo = np.concatenate([(a.sum()-a)/(len(a)-1)-b.mean(), a.mean()-(b.sum()-b)/(len(b)-1)])
    return {'effect':effect,'p':(int(extreme)+1)/(permutations+1),
            'ci95_unadjusted':np.quantile(boot,[.025,.975]).tolist(),
            'leave_one_out_range':[float(loo.min()),float(loo.max())]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True)
    p.add_argument('--spec', type=Path, required=True)
    p.add_argument('--cache', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        p.error('Refuse output overwrite')
    spec = json.loads(a.spec.read_text())
    files = {'archive':a.sources/'GSE135251_RAW.tar', 'metadata':a.sources/'GSE135251_family.xml.tgz', 'spec':a.spec, 'code':Path(__file__)}
    provenance = {k:sha(v) for k,v in files.items()}
    rows = metadata(files['metadata'])
    genes = spec['genes']
    start, cpu = time.monotonic(), time.process_time()
    cache_used = a.cache.exists()
    if cache_used:
        cache = json.loads(a.cache.read_text())
        if cache['inputs'] != provenance:
            raise ValueError('Stale cache')
        body = json.dumps(cache['data'],sort_keys=True).encode()
        if hashlib.sha256(body).hexdigest() != cache['payload_sha256']:
            raise ValueError('Corrupt cache')
        data = cache['data']
    else:
        data = []
        with tarfile.open(files['archive']) as tar:
            members = tar.getmembers()
            names = [m.name for m in members]
            if len(names) != len(set(names)) or set(names) != {r['file'] for r in rows}:
                raise ValueError('Archive/metadata mismatch')
            for r in rows:
                mark = time.process_time()
                with gzip.open(tar.extractfile(r['file']), 'rt') as f:
                    total, v, n = counts(f, set(genes.values()))
                data.append({'id':r['id'],'total':total,'genes':v,'features':n})
                time.sleep(max(0, (time.process_time()-mark)*4))
                if time.monotonic()-start > 600 or resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > 512*1024**2:
                    raise RuntimeError('Resource ceiling')
        body = json.dumps(data,sort_keys=True).encode()
        save(a.cache, {'inputs':provenance,'payload_sha256':hashlib.sha256(body).hexdigest(),'data':data})
    if [d['id'] for d in data] != [r['id'] for r in rows]:
        raise ValueError('Cache order mismatch')
    stages = np.array([r['stage'] for r in rows])
    nafld = np.array([r['disease']=='NAFLD' for r in rows])
    advanced, minimal = nafld & (stages>=3), nafld & (stages<=1)
    result = {'specification':spec['id'],'inputs':provenance,'cohort':{'libraries':len(rows),'NAFLD':int(nafld.sum()),'controls_excluded':int((~nafld).sum()),'stage_counts_NAFLD':dict(Counter(str(r['stage']) for r in rows if r['disease']=='NAFLD')),'advanced':int(advanced.sum()),'minimal':int(minimal.sum())},'qc':{'total_gene_count_range':[min(d['total'] for d in data),max(d['total'] for d in data)],'feature_counts':sorted(set(d['features'] for d in data))},'genes':{}}
    rng = np.random.Generator(np.random.PCG64(spec['tests']['seed']))
    for gene, gid in genes.items():
        mark = time.process_time()
        x = np.array([np.log2(1+1e6*d['genes'][gid]/d['total']) for d in data])
        r = statistics(x[advanced],x[minimal],rng)
        r['F3_vs_minimal_effect'] = float(x[nafld & (stages==3)].mean()-x[minimal].mean())
        r['stage_spearman_descriptive'] = float(np.corrcoef(ranks(stages[nafld]),ranks(x[nafld]))[0,1])
        r['zero_count_libraries'] = sum(d['genes'][gid]==0 for d in data)
        result['genes'][gene] = r
        time.sleep(max(0,(time.process_time()-mark)*4))
    for r,q in zip(result['genes'].values(),bh([r['p'] for r in result['genes'].values()])):
        r['bh_q_six_genes'] = float(q)
    result['pair_association_rule_met'] = all(result['genes'][g]['effect']>0 and result['genes'][g]['bh_q_six_genes']<.05 and result['genes'][g]['ci95_unadjusted'][0]>0 for g in spec['primary_targets'])
    save(a.out,result)
    save(Path(str(a.out)+'.execution.json'),{'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'cache_used':cache_used,'python':__import__('platform').python_version(),'numpy':np.__version__,'result_sha256':sha(a.out)})
    print(json.dumps({'result_sha256':sha(a.out),'pair_association_rule_met':result['pair_association_rule_met'],'cohort':result['cohort']}))


if __name__ == '__main__':
    main()
