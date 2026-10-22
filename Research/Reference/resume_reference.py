#!/usr/bin/env python3
"""Verify and resume the frozen technical follow-up; never overwrite a run."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import shutil
import sys
import time

import analyze_benchmark as analysis
import run_benchmark as runner

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + f'.{os.getpid()}.tmp')
    try:
        with temporary.open('x') as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def load_spec(path):
    spec = json.loads(path.read_text())
    if runner.digest(path) != path.with_suffix('.sha256').read_text().split()[0]:
        raise ValueError('Frozen follow-up specification digest mismatch')
    runner.verify_sources()
    return spec


def inspect(output, spec):
    jobs = runner.make_jobs(spec)
    _, models = analysis.verify_provenance(output, spec)
    statuses = []
    for job in jobs:
        state, _, _ = analysis.load_run(output, job, spec, models[job['file']])
        # An existing partial/invalid folder is evidence, never an automatic retry.
        if state['analysis_status'] == 'missing' and (output / job['job_id']).exists():
            state['analysis_status'] = 'invalid_input'
            state['reason'] = 'Existing unfinished folder; retain and investigate before a new protocol.'
        statuses.append(state)
    return jobs, statuses


def reuse_baseline(output, spec):
    reuse = spec['reuse']
    source = HERE / reuse['results']
    source_spec = json.loads((source / 'specification.json').read_text())
    if runner.digest(source / 'specification.json') != reuse['snapshot_sha256']:
        raise ValueError('Historical specification changed')
    analysis.verify_provenance(source, source_spec)
    job = runner.make_jobs(spec)[0]
    folder = source / job['job_id']
    provenance = verify_baseline_manifest(folder, reuse)
    state, _, _ = analysis.load_run(source, job, spec, reuse['model_sha256'])
    trace_hash = reuse['trace_sha256']
    if provenance != 'original_bytes_verified':
        receipt = json.loads((folder / 'manifest-redaction.json').read_text())
        trace_hash = receipt['published_trace_sha256']
    if state['analysis_status'] != 'eligible' or state['trace_sha256'] != trace_hash:
        raise ValueError('Historical baseline is not eligible for reuse')
    shutil.copytree(folder, output / job['job_id'])


def verify_baseline_manifest(folder, reuse):
    actual = runner.digest(folder / 'run.json')
    if actual == reuse['run_manifest_sha256']:
        return 'original_bytes_verified'
    receipt = folder / 'manifest-redaction.json'
    if not receipt.exists():
        raise ValueError('Historical baseline manifest changed')
    export = json.loads(receipt.read_text())
    if (export.get('original_sha256') != reuse['run_manifest_sha256']
            or export.get('published_sha256') != actual
            or export.get('changed_fields') not in (['argv[0]', 'argv[1]', 'argv[11]'], ['argv[0]', 'argv[1]', 'argv[11]', 'trace_sha256'])
            or export.get('trace_sha256') != reuse['trace_sha256']):
        raise ValueError('Historical baseline manifest changed or invalid redaction receipt')
    trace = (folder / 'trace.csv').read_bytes()
    numeric = b''.join(line for line in trace.splitlines(keepends=True) if not line.startswith(b'#'))
    if (analysis.sha256_bytes(trace) != export.get('published_trace_sha256')
            or analysis.sha256_bytes(numeric) != export.get('numeric_payload_sha256')):
        raise ValueError('Published trace or numeric payload differs from redaction receipt')
    # This verifies published bytes, not the withheld original path strings.
    return 'published_bytes_verified_original_digest_is_exporter_attestation'


def consumed_seconds(output, spec):
    used = 0.0
    for job in runner.make_jobs(spec)[1:]:
        path = output / job['job_id'] / 'run.json'
        if path.exists():
            record = json.loads(path.read_text())
            if 'wall_seconds' not in record:
                raise ValueError('Interrupted run has unknown cost; no automatic continuation')
            used += record['wall_seconds']
    return used


def save_status(output, spec):
    _, states = inspect(output, spec)
    try:
        used, cost_error = consumed_seconds(output, spec), None
    except ValueError as error:
        used, cost_error = None, str(error)
    status = {'updated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'benchmark': spec['version'], 'jobs': states,
              'remaining_jobs': [s['job_id'] for s in states if s['analysis_status'] == 'missing'],
              'blocked_jobs': [s['job_id'] for s in states if s['analysis_status'] not in ('eligible', 'missing')],
              'new_simulation_seconds': used, 'cost_error': cost_error,
              'checkpoint_unit': 'complete verified run; no CSV-to-RNG restart'}
    baseline = output / runner.make_jobs(spec)[0]['job_id']
    if baseline.exists():
        status['baseline_manifest_provenance'] = verify_baseline_manifest(baseline, spec['reuse'])
    atomic_json(output / 'resume-state.json', status)
    state_path = PROJECT / 'RESEARCH_STATE.json'
    if state_path.exists():
        project_state = json.loads(state_path.read_text())
        project_state['updated_utc'] = status['updated_utc']
        project_state['technical_followup'] = status
        atomic_json(state_path, project_state)
    return status


def execute(output, spec, spec_path, executable):
    runtime = json.loads((HERE / 'runtime-lock.json').read_text())
    if runner.digest(executable) != runtime['executable_sha256']:
        raise ValueError('KaSim executable differs from pinned runtime')
    output.mkdir(parents=True, exist_ok=True)
    with (output / '.resume.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        environment = output / 'environment.json'
        if not environment.exists():
            if any(p.name != '.resume.lock' for p in output.iterdir()):
                raise ValueError('Nonempty output without environment; do not overwrite')
            atomic_json(output / 'specification.json', spec)
            atomic_json(environment, {
                'benchmark_sha256': runner.digest(spec_path), 'runtime': runtime,
                'python': sys.version, 'platform': list(os.uname()),
                'runner_sha256': runner.digest(HERE / 'run_benchmark.py'),
                'resume_runner_sha256': runner.digest(__file__),
                'source_lock_sha256': runner.digest(HERE / 'source-lock.json'),
                'reuse': spec['reuse']})
            reuse_baseline(output, spec)
        else:
            if json.loads((output / 'specification.json').read_text()) != spec:
                raise ValueError('Existing output belongs to a different specification')
            recorded = json.loads(environment.read_text())
            if recorded.get('runtime') != runtime:
                raise ValueError('Recorded runtime differs from the pinned runtime')
            if recorded.get('resume_runner_sha256') != runner.digest(__file__):
                raise ValueError('Resume runner changed after execution began')
            if recorded.get('runner_sha256') != runner.digest(HERE / 'run_benchmark.py'):
                raise ValueError('Underlying benchmark runner changed after execution began')
        if not (output / runner.make_jobs(spec)[0]['job_id']).exists():
            reuse_baseline(output, spec)
        jobs, states = inspect(output, spec)
        if any(s['analysis_status'] not in ('eligible', 'missing') for s in states):
            save_status(output, spec)
            raise ValueError('Existing invalid or incomplete run retained; no automatic retry')
        for job, state in zip(jobs, states):
            if state['analysis_status'] == 'eligible':
                print(f"verified; skipped {job['job_id']}", flush=True)
                continue
            remaining = spec['budget']['total_simulation_wall_seconds'] - consumed_seconds(output, spec)
            if remaining < spec['budget']['per_run_timeout_seconds']:
                raise ValueError('Insufficient remaining budget for a complete timeout window')
            record = runner.run_job(job, spec, executable, output, time.monotonic() + remaining)
            save_status(output, spec)
            print(f"{job['job_id']}: {record['status']} ({record.get('wall_seconds', 0):.2f}s)", flush=True)
            if record['status'] != 'completed':
                return 1
        status = save_status(output, spec)
        print(json.dumps({'remaining_jobs': status['remaining_jobs'], 'blocked_jobs': status['blocked_jobs']}))
        return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, default=HERE / 'benchmark-v1.2.0.json')
    parser.add_argument('--output', type=Path, default=HERE / 'results/technical-v1.2')
    parser.add_argument('--kasim', type=Path)
    parser.add_argument('--execute', action='store_true', help='Run only missing jobs, through the host coordinator when configured')
    args = parser.parse_args(argv)
    spec = load_spec(args.spec.resolve())
    output = args.output.resolve()
    if args.execute:
        if args.kasim is None:
            parser.error('--execute requires --kasim')
        return execute(output, spec, args.spec.resolve(), args.kasim.resolve())
    _, states = inspect(output, spec)
    print(json.dumps({'mode': 'read_only_check', 'jobs': states}, indent=2))
    return 1 if any(s['analysis_status'] not in ('eligible', 'missing') for s in states) else 0


if __name__ == '__main__':
    raise SystemExit(main())
