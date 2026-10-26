#!/usr/bin/env python3
"""Frozen, bounded post-withdrawal Kappa experiment; completed runs are resume units."""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import time
from run_benchmark import digest, read_trace, at_time, write_json

HERE = Path(__file__).resolve().parent


def trace_hash_matches(path, expected):
    if digest(path) == expected:
        return True
    # Public copies remove only KaSim comment headers containing local paths.
    mapping = HERE / 'public-trace-map.json'
    if not mapping.exists():
        return False
    item = json.loads(mapping.read_text()).get(str(path.relative_to(HERE)), {})
    numeric = hashlib.sha256(json.dumps(read_trace(path), sort_keys=True).encode()).hexdigest()
    return (item.get('original_sha256') == expected and
            item.get('published_sha256') == digest(path) and item.get('numeric_sha256') == numeric)


def extended_trace(path):
    rows = read_trace(path)
    keys = list(rows[0])
    assert len(keys) == 16 and keys[11:14] == ['iHSC_early','TGFB1_free_total','TGFB1_bound_total']
    # KaSim labels constant observables by expression value, not the %obs alias.
    for row in rows:
        row['react_fate_fraction'] = row.pop(keys[14])
        row['react_exit_fraction_sum'] = row.pop(keys[15])
    return rows


def accepted_record(folder):
    record = json.loads((folder / 'run.json').read_text())
    receipt = folder / 'revalidation.json'
    if record['status'] == 'invalid_output' and receipt.exists():
        verified = json.loads(receipt.read_text())
        assert verified['run_manifest_sha256'] == digest(folder/'run.json')
        assert verified['verifier_sha256'] == digest(__file__)
        assert verified['trace_sha256'] == record['trace_sha256']
        assert record['returncode'] == 0 and record['validation_error'] == "KeyError: 'react_exit_fraction_sum'"
        record = {**record,'status':'completed','format_revalidated':True}
    return record


def specification():
    spec = json.loads((HERE / 'spec.json').read_text())
    assert digest(HERE / 'spec.json') == (HERE / 'spec.sha256').read_text().split()[0]
    assert digest(HERE / 'models/original.ka') == spec['original_sha256']
    for name, expected in spec['models'].items():
        assert digest(HERE / f'models/{name}.ka') == expected
    for seed, entry in spec['archive'].items():
        assert trace_hash_matches(HERE / f'archive/control-{seed}.csv', entry['trace_sha256'])
    return spec


def validate(rows, job):
    assert rows[0]['COL1 tot'] == .5 and rows[-1]['[T]'] >= 90
    assert all(v >= 0 for row in rows for v in row.values())
    for row in rows:
        assert abs(row['react_exit_fraction_sum'] - 1) < 1e-12
        if row['[T]'] < 60 or job['model'] == 'control':
            assert row['react_fate_fraction'] == .05
        elif row['[T]'] > 60:
            assert row['react_fate_fraction'] == .5


def execute(job_id, executable):
    spec = specification()
    assert digest(executable) == spec['runtime']['executable_sha256']
    job = next(x for x in spec['jobs'] if x['id'] == job_id)
    out = HERE / 'results'; out.mkdir(exist_ok=True)
    folder = out / job_id
    if folder.exists():
        record = accepted_record(folder)
        assert record['status'] == 'completed', 'Incomplete run retained; no automatic retry'
        assert record['spec_sha256'] == digest(HERE / 'spec.json')
        assert record.get('format_revalidated') or record['runner_sha256'] == digest(__file__)
        assert trace_hash_matches(folder / 'trace.csv', record['trace_sha256'])
        validate(extended_trace(folder / 'trace.csv'), job)
        print(job_id + ': verified existing result; no new simulation')
        return
    consumed = sum(json.loads(f.read_text()).get('wall_seconds', 0) for f in out.glob('*/run.json'))
    assert spec['budget']['total_new_run_seconds'] - consumed >= spec['budget']['per_run_seconds']
    assert sum(f.stat().st_size for f in out.rglob('*') if f.is_file()) < spec['budget']['max_output_MB'] * 1000000
    folder.mkdir()
    model = HERE / ('models/' + job['model'] + '.ka')
    cmd = [str(executable.resolve()), str(model), '-l', '90', '-p', str(job['period']),
           '-seed', str(job['seed']), '-mode', 'batch', '-d', str(folder), '-o', 'trace.csv',
           '-log', 'inputs', '--print-efficiency', '--gluttony']
    record = {**job, 'status': 'started', 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'spec_sha256': digest(HERE / 'spec.json'), 'runner_sha256': digest(__file__),
              'model_sha256': digest(model), 'runtime_sha256': digest(executable),
              'python': platform.python_version(), 'platform': platform.platform(),
              'command_template': 'KaSim models/MODEL.ka -l90 -pPERIOD -seedSEED -mode batch -dOUTPUT -otrace.csv -loginputs --print-efficiency --gluttony'}
    write_json(folder / 'run.json', record)
    start = time.monotonic()
    # KaSim stays in the coordinator's process group; no detached descendants.
    with (folder / 'stdout.private.log').open('w') as log:
        process = subprocess.Popen(cmd, cwd=folder, stdout=log, stderr=subprocess.STDOUT)
        try:
            process.wait(timeout=spec['budget']['per_run_seconds'])
            record['status'] = 'completed' if process.returncode == 0 else 'runtime_error'
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
            record['status'] = 'timeout'
    record.update(wall_seconds=time.monotonic() - start, returncode=process.returncode)
    if (folder / 'trace.csv').exists():
        record['trace_sha256'] = digest(folder / 'trace.csv')
        try:
            rows = extended_trace(folder / 'trace.csv')
            record.update(rows=len(rows), last_day=rows[-1]['[T]'])
            validate(rows, job)
        except (AssertionError, ValueError, KeyError) as error:
            record['validation_error'] = type(error).__name__ + ': ' + str(error)
            if record['status'] == 'completed': record['status'] = 'invalid_output'
    elif record['status'] == 'completed': record['status'] = 'missing_output'
    write_json(folder / 'run.json', record)
    print(json.dumps({k: record[k] for k in ['id', 'status', 'wall_seconds', 'returncode']}), flush=True)
    if record['status'] != 'completed': raise SystemExit(1)


def common_error(a, b, before=None):
    # Duplicate boundary rows are excluded; regular shared observations are compared.
    aa = {r['[T]']: r for r in a if before is None or r['[T]'] < before}
    bb = {r['[T]']: r for r in b if before is None or r['[T]'] < before}
    times = sorted(aa.keys() & bb.keys())
    assert times
    keys = set(a[0]) & set(b[0]) - {'[T]'}
    return {'shared_times': len(times), 'maximum_absolute_difference':
            max(abs(aa[t][k] - bb[t][k]) for t in times for k in keys)}


def component(t, fate, half, early_half=.75, inactive_half=730):
    """Exact probabilities for the explicitly conditional A -> E -> I chain."""
    k, mu, delta = [math.log(2) / h for h in (half, early_half, inactive_half)]
    assert 0 <= fate <= 1 and t >= 0 and len({k, mu, delta}) == 3
    active = math.exp(-k*t)
    early = fate*k*(math.exp(-k*t)-math.exp(-mu*t))/(mu-k)
    inactive = fate*k*mu*sum(math.exp(-r*t) / math.prod(s-r for s in [k, mu, delta] if s != r)
                           for r in [k, mu, delta])
    return {'active': active, 'early_inactive': early, 'inactive': inactive,
            'removed': 1-active-early-inactive}


def analyze():
    spec = specification(); out = HERE / 'results'; out.mkdir(exist_ok=True)
    records = {p.parent.name: accepted_record(p.parent) for p in out.glob('*/run.json')}
    for key,record in records.items():
        if record['status'] == 'completed':
            assert trace_hash_matches(out/key/'trace.csv',record['trace_sha256'])
    traces = {k: extended_trace(out/k/'trace.csv') for k,v in records.items() if v['status'] == 'completed'}
    archive = {s: read_trace(HERE/f'archive/control-{s}.csv') for s in spec['primary_seeds']}
    checks = {}
    if 'control-101' in traces: checks['instrumentation'] = common_error(traces['control-101'], archive[101])
    if 'replay-101' in traces and 'fate50-101' in traces:
        checks['seed_replay_exact'] = traces['replay-101'] == traces['fate50-101']
    if 'grid-101' in traces and 'fate50-101' in traces:
        checks['observation_grid'] = common_error(traces['grid-101'], traces['fate50-101'])
    endpoints = []
    for seed in spec['primary_seeds']:
        name = f'fate50-{seed}'
        if name not in traces: continue
        checks[f'preintervention-{seed}'] = common_error(traces[name], archive[seed], before=60)
        for day in [60,65,75,90]:
            a,b = at_time(archive[seed],day), at_time(traces[name],day)
            for key in ['COL1 tot','aSMA-cells','react_MFB','iHSC']:
                endpoints.append({'seed':seed,'requested_day':day,'control_observed_day':a['[T]'],
                    'scenario_observed_day':b['[T]'],'observable':key,'control':a[key],
                    'scenario':b[key],'difference':b[key]-a[key]})
    complete = all(f'fate50-{s}' in traces for s in spec['primary_seeds'])
    summary = {}
    if complete:
        for key in ['COL1 tot','aSMA-cells','react_MFB','iHSC']:
            values=[x['difference'] for x in endpoints if x['requested_day']==90 and x['observable']==key]
            summary[key]={'mean_difference':sum(values)/len(values),'min_difference':min(values),'max_difference':max(values),'n_seeds':len(values)}
    result={'spec_sha256':digest(HERE/'spec.json'),'statuses':{k:v['status'] for k,v in records.items()},
            'technical_checks':checks,'endpoints':endpoints,'three_seed_condition_complete':complete,
            'day90_descriptive_pilot':summary,'independent_biological_validation':'not performed',
            'measurement_uncertainty':'unknown, no new biological observations','parameter_uncertainty':'not estimated',
            'treatment_effect':'not estimated; fate50 is an experimental parameter setting'}
    write_json(out/'analysis.json',result)
    c=spec['conditional_component']; grid=[]
    for half in c['exit_half_life_days']:
        for lifespan in c['inactive_half_life_days']:
            for fate in c['fate_fraction']:
                for day in c['readout_days']:
                    grid.append({'exit_half_days':half,'inactive_half_days':lifespan,'fate_fraction':fate,'day':day,
                                 **component(day,fate,half,inactive_half=lifespan)})
    with (out/'conditional-grid.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(grid[0]));writer.writeheader();writer.writerows(grid)
    print(json.dumps({'checks':checks,'complete':complete,'day90':summary,'conditional_grid_rows':len(grid)},indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', choices=[j['id'] for j in specification()['jobs']])
    parser.add_argument('--kasim',type=Path)
    parser.add_argument('--analyze',action='store_true')
    args=parser.parse_args()
    if args.run:
        if args.kasim is None: parser.error('--kasim required with --run')
        execute(args.run,args.kasim)
    if args.analyze: analyze()
