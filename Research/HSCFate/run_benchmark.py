#!/usr/bin/env python3
"""Run the frozen benchmark through the original KaSim executable. Python stdlib only."""
import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_trace(path):
    with Path(path).open() as stream:
        reader = csv.DictReader(line for line in stream if not line.startswith('#'))
        if not reader.fieldnames:
            raise ValueError('Missing CSV header')
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('CSV row width differs from header')
            rows.append({key.strip("'"): float(value) for key, value in row.items()})
    required = {'[T]', 'COL1 tot', 'qHSC', 'iHSC', 'aSMA-cells'}
    if not rows or not required.issubset(rows[0]):
        raise ValueError('Missing observations')
    if any(not math.isfinite(value) for row in rows for value in row.values()):
        raise ValueError('Nonfinite observation')
    if any(a['[T]'] > b['[T]'] for a, b in zip(rows, rows[1:])):
        raise ValueError('Time went backwards')
    return rows


def at_time(rows, requested):
    if requested < rows[0]['[T]'] or requested > rows[-1]['[T]']:
        raise ValueError('Extrapolation is forbidden')
    return next(row for row in reversed(rows) if row['[T]'] <= requested)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def verify_sources():
    lock = json.loads((HERE / 'source-lock.json').read_text())
    for item in lock['artifacts']:
        if item['repository'].endswith('/HSC_model_Kappa'):
            path = HERE / 'vendor/HSC_model_Kappa' / item['path']
            if digest(path) != item['sha256']:
                raise ValueError(f'Original source changed: {path.name}')


def make_jobs(spec):
    jobs = []
    for condition in spec['conditions']:
        for seed in condition['seeds']:
            jobs.append({**condition, 'seed': seed,
                         'job_id': f"{condition['id']}-{seed}",
                         'period': spec['sampling']['period_days']})
    original = jobs[0]
    jobs.append({**original, 'job_id': 'seed-replay-101'})
    jobs.append({**original, 'job_id': 'grid-quarter-day-101', 'period': 0.25})
    if len(jobs) > spec['budget']['maximum_runs']:
        raise ValueError('Job count exceeds frozen budget')
    return jobs


def run_job(job, spec, executable, output, deadline):
    folder = output / job['job_id']
    folder.mkdir()
    model = HERE / 'vendor/HSC_model_Kappa' / job['file']
    cmd = [str(executable), str(model), '-l', str(spec['sampling']['duration_limit_days']),
           '-p', str(job['period']), '-seed', str(job['seed']), '-mode', 'batch',
           '-d', str(folder), '-o', 'trace.csv', '-log', 'inputs', '--print-efficiency']
    cmd.extend(spec.get('runtime_arguments', []))
    for name, value in sorted(job['overrides'].items()):
        cmd.extend(['-var', name, str(value)])
    record = {'job_id': job['job_id'], 'condition': job['id'], 'seed': job['seed'],
              'model_sha256': digest(model), 'argv': cmd, 'overrides': job['overrides'],
              'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'period_days': job['period'], 'status': 'not_started'}
    write_json(folder / 'run.json', record)
    remaining = deadline - time.monotonic()
    size = sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
    if remaining <= 0 or size > spec['budget']['maximum_output_megabytes'] * 1_000_000:
        record['status'] = 'budget_exhausted'
        write_json(folder / 'run.json', record)
        return record
    timeout = min(remaining, spec['budget']['per_run_timeout_seconds'])
    start = time.monotonic()
    with (folder / 'stdout.log').open('w') as log:
        process = subprocess.Popen(cmd, cwd=folder, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            process.wait(timeout=timeout)
            record['status'] = 'completed' if process.returncode == 0 else 'runtime_error'
        except subprocess.TimeoutExpired:
            record['status'] = 'timeout'
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        record['returncode'] = process.returncode
    record['wall_seconds'] = time.monotonic() - start
    trace = folder / 'trace.csv'
    if trace.exists():
        record['trace_sha256'] = digest(trace)
        try:
            rows = read_trace(trace)
            record['rows'] = len(rows)
            record['last_day'] = rows[-1]['[T]']
            record['minimum_observation'] = min(v for row in rows for k, v in row.items() if k != '[T]')
            record['initial_collagen'] = rows[0]['COL1 tot']
            if rows[-1]['[T]'] < 240 or rows[0]['COL1 tot'] != 0.5:
                raise ValueError('Incomplete time coverage or unexpected initial collagen')
        except (ValueError, KeyError, TypeError) as error:
            record['validation_error'] = str(error)
            if record['status'] == 'completed':
                record['status'] = 'invalid_output'
    elif record['status'] == 'completed':
        record['status'] = 'missing_output'
    write_json(folder / 'run.json', record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kasim', required=True, type=Path)
    parser.add_argument('--spec', type=Path, default=HERE / 'benchmark-v1.1.0.json')
    parser.add_argument('--output', required=True, type=Path,
                        help='New directory; existing results are never overwritten')
    args = parser.parse_args()
    executable, output = args.kasim.resolve(), args.output.resolve()
    spec_path = args.spec.resolve()
    expected = spec_path.with_suffix('.sha256').read_text().split()[0]
    if digest(spec_path) != expected:
        raise ValueError('Frozen specification hash mismatch')
    verify_sources()
    spec = json.loads(spec_path.read_text())
    runtime = json.loads((HERE / 'runtime-lock.json').read_text())
    if digest(executable) != runtime['executable_sha256']:
        raise ValueError('Runtime differs from pinned executable; requires a new benchmark version')
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'specification.json', spec)
    write_json(output / 'environment.json', {
        'benchmark_sha256': expected, 'runtime': runtime, 'python': os.sys.version,
        'platform': os.uname()._asdict() if hasattr(os.uname(), '_asdict') else list(os.uname()),
        'runner_sha256': digest(__file__), 'source_lock_sha256': digest(HERE / 'source-lock.json')})
    deadline = time.monotonic() + spec['budget']['total_simulation_wall_seconds']
    jobs = make_jobs(spec)
    records = [run_job(jobs[0], spec, executable, output, deadline)]
    write_json(output / 'execution.json', records)
    if records[0]['status'] != 'completed':
        print('Initial full original run failed; stopped without lowering biological scope.', flush=True)
        return 1
    print(f"{records[0]['job_id']}: completed in {records[0]['wall_seconds']:.2f}s", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=spec['budget']['maximum_workers']) as pool:
        futures = [pool.submit(run_job, job, spec, executable, output, deadline) for job in jobs[1:]]
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            records.append(record)
            write_json(output / 'execution.json', records)
            print(f"{record['job_id']}: {record['status']} ({record.get('wall_seconds', 0):.2f}s)", flush=True)
    return 0 if all(record['status'] == 'completed' for record in records) else 1


if __name__ == '__main__':
    raise SystemExit(main())
