#!/usr/bin/env python3
"""Verify archived controls and execute at most one missing frozen mechanism run."""
import argparse
import datetime as dt
import fcntl
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time

import resume_reference as resume

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
runner = resume.runner
analysis = resume.analysis


def reuse_runs(output, spec):
    jobs = {job['job_id']: job for job in runner.make_jobs(spec)}
    for name, reuse in spec['reuse_runs'].items():
        if name not in jobs:
            raise ValueError('Unknown reused job')
        if (output / name).exists():
            resume.verify_baseline_manifest(output / name, reuse)
            continue  # Existing folders are subsequently verified, never overwritten.
        source = (HERE / reuse['results']).resolve()
        if not source.is_relative_to(HERE / 'results') or source == output.resolve():
            raise ValueError('Invalid archive location')
        snapshot = source / 'specification.json'
        if runner.digest(snapshot) != reuse['snapshot_sha256']:
            raise ValueError('Archive specification changed')
        analysis.verify_provenance(source, json.loads(snapshot.read_text()))
        folder = source / name
        provenance = resume.verify_baseline_manifest(folder, reuse)
        state, _, _ = analysis.load_run(source, jobs[name], spec, reuse['model_sha256'])
        trace_hash = reuse['trace_sha256']
        if provenance != 'original_bytes_verified':
            trace_hash = json.loads((folder / 'manifest-redaction.json').read_text())['published_trace_sha256']
        if state['analysis_status'] != 'eligible' or state['trace_sha256'] != trace_hash:
            raise ValueError('Archive run is not eligible')
        target = output / name
        target.mkdir()
        for filename in ('run.json', 'trace.csv', 'manifest-redaction.json'):
            if (folder / filename).exists():
                shutil.copyfile(folder / filename, target / filename)


def consumed_seconds(output, spec):
    used = 0.0
    for job in runner.make_jobs(spec):
        if job['job_id'] in spec['reuse_runs']:
            continue
        path = output / job['job_id'] / 'run.json'
        if path.exists():
            cost = json.loads(path.read_text()).get('wall_seconds')
            if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
                raise ValueError('Unknown or invalid previous simulation cost')
            used += cost
    return used


def next_job(output, spec):
    jobs, states = resume.inspect(output, spec)
    if any(s['analysis_status'] not in ('eligible', 'missing') for s in states):
        raise ValueError('Incomplete or invalid run retained; no automatic retry')
    missing = [job for job, state in zip(jobs, states) if state['analysis_status'] == 'missing']
    if any(job['job_id'] in spec['reuse_runs'] for job in missing):
        raise ValueError('Archived control missing; never silently resimulate it')
    remaining = spec['budget']['total_simulation_wall_seconds'] - consumed_seconds(output, spec)
    if missing and remaining < spec['budget']['per_run_timeout_seconds']:
        raise ValueError('Insufficient budget for a complete timeout window')
    return missing[0] if missing else None, remaining


def save_status(output, spec):
    _, states = resume.inspect(output, spec)
    state = {'updated_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'benchmark': spec['version'],
             'jobs': states, 'new_simulation_seconds': consumed_seconds(output, spec),
             'remaining_jobs': [s['job_id'] for s in states if s['analysis_status'] == 'missing'],
             'blocked_jobs': [s['job_id'] for s in states if s['analysis_status'] not in ('eligible', 'missing')],
             'checkpoint_unit': 'complete verified run; no CSV-to-RNG restart',
             'scope': 'whole-course mechanism pilot; no drug, independent biological or clinical validation'}
    resume.atomic_json(output / 'resume-state.json', state)
    project_state = PROJECT / 'RESEARCH_STATE.json'
    if project_state.exists():
        current = json.loads(project_state.read_text())
        current['updated_utc'] = state['updated_utc']
        current['mechanism_pilot'] = state
        resume.atomic_json(project_state, current)
    return state


def execute_one(output, spec, spec_path, executable):
    runtime = json.loads((HERE / 'runtime-lock.json').read_text())
    if runner.digest(executable) != runtime['executable_sha256']:
        raise ValueError('Runtime differs from pinned executable')
    output.mkdir(parents=True, exist_ok=True)
    with (output / '.resume.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        expected = {'benchmark_sha256': runner.digest(spec_path), 'runtime': runtime,
                    'runner_sha256': runner.digest(HERE / 'run_benchmark.py'),
                    'pilot_runner_sha256': runner.digest(__file__),
                    'resume_helper_sha256': runner.digest(HERE / 'resume_reference.py'),
                    'source_lock_sha256': runner.digest(HERE / 'source-lock.json')}
        environment = output / 'environment.json'
        if not environment.exists():
            if any(p.name != '.resume.lock' for p in output.iterdir()):
                raise ValueError('Nonempty output without environment; retain and inspect')
            resume.atomic_json(output / 'specification.json', spec)
            resume.atomic_json(environment, {**expected, 'python': sys.version, 'platform': list(os.uname())})
        else:
            recorded = json.loads(environment.read_text())
            if any(recorded.get(key) != value for key, value in expected.items()):
                raise ValueError('Execution specification, source or runtime changed')
            if json.loads((output / 'specification.json').read_text()) != spec:
                raise ValueError('Stored specification changed')
        reuse_runs(output, spec)
        job, remaining = next_job(output, spec)
        if job is None:
            save_status(output, spec)
            print('All planned runs verified; no simulation executed.')
            return 0
        record = runner.run_job(job, spec, executable, output, time.monotonic() + remaining)
        state = save_status(output, spec)
        print(json.dumps({'executed_one': job['job_id'], 'status': record['status'],
                          'remaining_jobs': state['remaining_jobs'], 'blocked_jobs': state['blocked_jobs']}))
        completed = next(s for s in state['jobs'] if s['job_id'] == job['job_id'])
        return 0 if record['status'] == 'completed' and completed['analysis_status'] == 'eligible' and not state['blocked_jobs'] else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, default=HERE / 'benchmark-v1.3.0.json')
    parser.add_argument('--output', type=Path, default=HERE / 'results/mechanism-v1.3')
    parser.add_argument('--kasim', type=Path)
    parser.add_argument('--execute-one', action='store_true')
    args = parser.parse_args(argv)
    spec_path, output = args.spec.resolve(), args.output.resolve()
    spec = resume.load_spec(spec_path)
    if args.execute_one:
        if args.kasim is None:
            parser.error('--execute-one requires --kasim')
        return execute_one(output, spec, spec_path, args.kasim.resolve())
    _, states = resume.inspect(output, spec)
    print(json.dumps({'mode': 'read_only_check', 'jobs': states}, indent=2))
    return 1 if any(s['analysis_status'] not in ('eligible', 'missing') for s in states) else 0


if __name__ == '__main__':
    raise SystemExit(main())
