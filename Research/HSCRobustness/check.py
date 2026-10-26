"""Bounded follow-up of HSC fate: stochastic uncertainty and one alternative assumption."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'HSCFate'))
from run import common_error, extended_trace, accepted_record, trace_hash_matches
from run_benchmark import digest, read_trace, at_time, write_json


def runner_accepted(record):
    return record['runner_sha256'] in [digest(__file__), digest(HERE/'executed-check.py')]


def trace_matches(path, expected):
    if digest(path) == expected:
        return True
    mapping=HERE/'public-trace-map.json'
    if not mapping.exists():
        return False
    entry=json.loads(mapping.read_text()).get(str(path.relative_to(HERE)),{})
    numeric=hashlib.sha256(json.dumps(read_trace(path),sort_keys=True).encode()).hexdigest()
    return entry.get('original_sha256') == expected and entry.get('published_sha256') == digest(path) and entry.get('numeric_sha256') == numeric


def record_for(folder):
    record = json.loads((folder/'run.json').read_text())
    if record['status'] == 'invalid_output' and (folder/'revalidation.json').exists():
        receipt = json.loads((folder/'revalidation.json').read_text())
        assert record['returncode'] == 0 and record['error'] == 'AssertionError: '
        assert receipt['run_manifest_sha256'] == digest(folder/'run.json')
        assert receipt['checker_sha256'] == digest(__file__)
        assert receipt['trace_sha256'] == record['trace_sha256']
        assert receipt['reason'] == 'Sequential same-time parameter updates; unchanged biological state'
        record = {**record, 'status':'completed', 'output_event_revalidated':True}
    return record


def spec():
    p = HERE / 'spec.json'
    assert digest(p) == (HERE / 'spec.sha256').read_text().split()[0]
    s = json.loads(p.read_text())
    for item in s['models'].values():
        assert digest(HERE/item['path']) == item['sha256']
    for seed, item in s['archives'].items():
        assert digest(HERE/f'archive/control-{seed}.trace.csv') == item['published_trace_sha256']
        assert digest(HERE/f'archive/control-{seed}.run.json') == item['public_run_manifest_sha256']
    assert len(s['jobs']) * s['budget']['per_run_seconds'] <= s['budget']['total_new_run_seconds']
    return s


def rows_for(path):
    rows = read_trace(path)
    keys = list(rows[0])
    assert len(keys) in [16, 17] and keys[11:14] == ['iHSC_early', 'TGFB1_free_total', 'TGFB1_bound_total']
    for row in rows:
        row['react_fate_fraction'] = row.pop(keys[14])
        row['react_exit_fraction_sum'] = row.pop(keys[15])
        if len(keys) == 17:
            row['inactive_lifetime_days'] = row.pop(keys[16])
    return rows


def validate(rows, job, control):
    assert rows[0]['[T]'] == 0 and rows[0]['COL1 tot'] == .5 and rows[-1]['[T]'] >= 90
    assert {i / 2 for i in range(181)} <= {row['[T]'] for row in rows}, 'Incomplete 0.5-day output grid'
    assert any(row['[T]'] == 90 for row in control), 'Missing exact control endpoint'
    assert all(math.isfinite(v) and v >= 0 for row in rows for v in row.values())
    assert all(a['[T]'] <= b['[T]'] for a, b in zip(rows, rows[1:]))
    first_post = next(row['[T]'] for row in rows if row['[T]'] > 60)
    intermediate_count = 0
    for index, row in enumerate(rows):
        assert abs(row['react_exit_fraction_sum'] - 1) < 1e-12
        if row['[T]'] != 60:
            expected = .05 if row['[T]'] < 60 else job['fate_after']
            assert row['react_fate_fraction'] == expected
            if job['model'].startswith('lowpersist_'):
                lifetime = 730 if row['[T]'] < 60 else 30
                if row['inactive_lifetime_days'] != lifetime:
                    # Two $PLOTENTRY updates expose an intermediate state at the same event time.
                    assert job['model'] == 'lowpersist_fate50' and row['[T]'] == first_post
                    assert row['inactive_lifetime_days'] == 730 and lifetime == 30
                    assert index+1 < len(rows) and rows[index+1] == {**row,'inactive_lifetime_days':30}
                    intermediate_count += 1
                    assert intermediate_count == 1
    comparison = common_error(rows, control, before=60)
    assert comparison['maximum_absolute_difference'] <= 1e-8
    assert comparison['shared_times'] >= 120
    return comparison


def execute(job, executable):
    s = spec()
    assert digest(executable) == s['runtime_sha256']
    out = HERE/'results'/job['id']
    control = read_trace(HERE/f"archive/control-{job['seed']}.trace.csv")
    if out.exists():
        r = record_for(out)
        assert r['status'] == 'completed', 'Incomplete run retained; automatic retry prohibited'
        assert r['spec_sha256'] == digest(HERE/'spec.json') and runner_accepted(r)
        assert r['runtime_sha256'] == digest(executable) and r['model_sha256'] == s['models'][job['model']]['sha256']
        assert trace_matches(out/'trace.csv',r['trace_sha256'])
        validate(rows_for(out/'trace.csv'), job, control)
        return {'id': job['id'], 'reused': True}
    out.mkdir(parents=True)
    model = HERE/s['models'][job['model']]['path']
    r = {**job, 'status': 'started', 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
         'spec_sha256': digest(HERE/'spec.json'), 'runner_sha256': digest(__file__),
         'runtime_sha256': digest(executable), 'model_sha256': digest(model),
         'python': platform.python_version(), 'platform': platform.platform(),
         'command_template': 'KaSim MODEL -l 90 -p 0.5 -seed SEED -mode batch -d OUTPUT -o trace.csv -log inputs --print-efficiency --gluttony'}
    write_json(out/'run.json', r)
    cmd = [str(executable), str(model.resolve()), '-l', '90', '-p', '.5', '-seed', str(job['seed']),
           '-mode', 'batch', '-d', str(out), '-o', 'trace.csv', '-log', 'inputs', '--print-efficiency', '--gluttony']
    start = time.monotonic()
    with (out/'stdout.private.log').open('w') as log:
        process = subprocess.Popen(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT)
        try:
            process.wait(timeout=s['budget']['per_run_seconds'])
            r['status'] = 'completed' if process.returncode == 0 else 'runtime_error'
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
            r['status'] = 'timeout'
    r.update(wall_seconds=time.monotonic()-start, returncode=process.returncode)
    if (out/'trace.csv').exists():
        r['trace_sha256'] = digest(out/'trace.csv')
        if r['status'] == 'completed':
            try:
                rows = rows_for(out/'trace.csv')
                r['prehistory'] = validate(rows, job, control)
                r['last_day'] = rows[-1]['[T]']
            except (AssertionError, ValueError, KeyError) as error:
                r.update(status='invalid_output', error=type(error).__name__+': '+str(error))
    elif r['status'] == 'completed':
        r['status'] = 'missing_output'
    write_json(out/'run.json', r)
    print(json.dumps({k: r[k] for k in ['id', 'status', 'wall_seconds']}), flush=True)
    if r['status'] != 'completed':
        raise RuntimeError(job['id']+': '+r['status'])
    return r


def sign_interval(k, n, alpha=.05):
    """Exact Clopper-Pearson interval for P(difference > 0); zeros are non-positive."""
    assert n > 0 and 0 <= k <= n and 0 < alpha < 1
    def cdf(m, p):
        return sum(math.comb(n, j)*p**j*(1-p)**(n-j) for j in range(m+1))
    def inverse_cdf(m, target):
        lo, hi = 0., 1.
        for _ in range(70):
            mid = (lo+hi)/2
            if cdf(m, mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo+hi)/2
    return [0. if k == 0 else inverse_cdf(k-1, 1-alpha/2),
            1. if k == n else inverse_cdf(k, alpha/2)]


def quantile(values, p):
    ordered = sorted(values); x = (len(ordered)-1)*p; i = int(x); f = x-i
    return ordered[i]*(1-f)+ordered[min(i+1, len(ordered)-1)]*f


def summarize(values, samples, seed):
    assert len(values) >= 2 and all(math.isfinite(v) for v in values)
    rng = random.Random(seed); n = len(values)
    means = [statistics.fmean(values[rng.randrange(n)] for _ in range(n)) for _ in range(samples)]
    sd = statistics.stdev(values); k = sum(v > 0 for v in values)
    return {'n_seeds': n, 'mean': statistics.fmean(values), 'sd': sd, 'mc_standard_error': sd/math.sqrt(n),
            'mean_bootstrap_percentile_95': [quantile(means,.025), quantile(means,.975)],
            'minimum': min(values), 'maximum': max(values), 'positive': k,
            'zero': sum(v == 0 for v in values), 'positive_probability_CP95': sign_interval(k,n),
            'scope': 'Finite pseudorandom-seed Monte Carlo uncertainty, fixed parameters; exploratory, not measurement or parameter uncertainty'}


def analyze():
    s = spec(); out = HERE/'results'; traces = {}; records = {}
    for job in s['jobs']:
        folder = out/job['id']; r = record_for(folder)
        assert r['status'] == 'completed' and r['spec_sha256'] == digest(HERE/'spec.json')
        assert runner_accepted(r) and trace_matches(folder/'trace.csv',r['trace_sha256'])
        assert r['runtime_sha256'] == s['runtime_sha256'] and r['model_sha256'] == s['models'][job['model']]['sha256']
        trace = rows_for(folder/'trace.csv'); validate(trace, job, read_trace(HERE/f"archive/control-{job['seed']}.trace.csv"))
        traces[job['id']] = trace; records[job['id']] = r
    for seed in [101,102,103]:
        folder=HERE.parent/'HSCFate/results'/f'fate50-{seed}'; r=accepted_record(folder)
        assert r['status'] == 'completed' and trace_hash_matches(folder/'trace.csv',r['trace_sha256'])
        assert r['model_sha256'] == s['models']['fate50']['sha256'] and r['runtime_sha256'] == s['runtime_sha256']
        traces[f'fate50-{seed}'] = extended_trace(folder/'trace.csv')
        validate(traces[f'fate50-{seed}'], {'model':'fate50','fate_after':.5}, read_trace(HERE/f'archive/control-{seed}.trace.csv'))
    differences=[]
    for seed in range(101,111):
        control=at_time(read_trace(HERE/f'archive/control-{seed}.trace.csv'),90)
        scenario=at_time(traces[f'fate50-{seed}'],90)
        for key in s['observables']:
            differences.append({'seed':seed,'observable':key,'control':control[key],'scenario':scenario[key],'difference':scenario[key]-control[key]})
    summary={}
    for label,seeds in [('all10',range(101,111)),('new_extension7',range(104,111))]:
        summary[label]={key:summarize([d['difference'] for d in differences if d['observable']==key and d['seed'] in seeds],s['bootstrap_resamples'],s['bootstrap_seed']) for key in s['observables']}
    corners=[]
    for seed in [101,102]:
        a=at_time(traces[f'lowpersist_control-{seed}'],90); b=at_time(traces[f'lowpersist_fate50-{seed}'],90)
        for key in s['observables']:
            original=next(d['difference'] for d in differences if d['seed']==seed and d['observable']==key)
            corners.append({'seed':seed,'observable':key,'control':a[key],'scenario':b[key],'difference':b[key]-a[key],'original_difference':original,'sign_agrees':(b[key]-a[key])*original>0})
    write_json(out/'analysis.json',{'spec_sha256':digest(HERE/'spec.json'),'all_new_jobs_complete':True,'new_run_count':len(records),'new_run_wall_seconds':sum(r['wall_seconds'] for r in records.values()),'differences':differences,'summary':summary,'alternative_assumption':corners,'parameter_posterior':'Not identifiable from available observations; not estimated','biological_validation':False,'drug_parameter_mapping':False,'laboratory_forwarding':'withheld pending evidence gaps; user instruction'})
    print(json.dumps({'complete':True,'summary':summary,'alternative':corners},indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',action='store_true');parser.add_argument('--run');parser.add_argument('--kasim',type=Path);parser.add_argument('--analyze',action='store_true')
    args=parser.parse_args()
    if args.batch or args.run:
        assert args.kasim is not None
        s=spec(); jobs=[j for j in s['jobs'] if not args.run or j['id']==args.run];assert jobs
        assert sum(j.get('wall_seconds',0) for j in [json.loads(p.read_text()) for p in (HERE/'results').glob('*/run.json')]) <= s['budget']['total_new_run_seconds']
        if args.batch:
            # Fixed at most 11 jobs x 600 s, two workers; no adaptive retry or detached process.
            with ThreadPoolExecutor(max_workers=s['budget']['workers']) as pool:
                list(pool.map(lambda job:execute(job,args.kasim),jobs))
        else:
            execute(jobs[0],args.kasim)
    if args.analyze:analyze()
