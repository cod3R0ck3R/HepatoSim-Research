#!/usr/bin/env python3
"""One bounded Goose task on an already installed, confirmed local Ollama model."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import time
import urllib.request

ENDPOINT = 'http://127.0.0.1:11434/api/'


def api(route, payload=None):
    request = urllib.request.Request(ENDPOINT + route,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def validate_model(tags, name, digest, details):
    matches = [m for m in tags.get('models', []) if m['name'] == name and m['digest'] == digest]
    if len(matches) != 1:
        raise ValueError('Requested installed model/digest not found; downloads are forbidden')
    if any(obj.get(key) for obj in [matches[0], details] for key in ('remote_model', 'remote_host')):
        raise ValueError('Remote model is forbidden')
    if details.get('details', {}).get('format') != 'gguf':
        raise ValueError('Expected a locally installed GGUF model')
    return matches[0]


def local_runners():
    rows = subprocess.check_output(['ps', '-axo', 'pid=,rss=,%cpu=,command='], text=True).splitlines()
    found = []
    for row in rows:
        parts = row.strip().split(None, 3)
        if len(parts) != 4 or 'ollama runner' not in parts[3]:
            continue
        argv = shlex.split(parts[3])
        if '--model' not in argv:
            continue
        blob = Path(argv[argv.index('--model') + 1])
        found.append({'pid': int(parts[0]), 'rss_kib': int(parts[1]), 'cpu_percent': float(parts[2]),
                      'model_blob_name': blob.name, 'model_blob_exists': blob.is_file(),
                      'model_blob_bytes': blob.stat().st_size if blob.is_file() else 0})
    return found


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True)
    p.add_argument('--digest', required=True)
    p.add_argument('--task', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True, help='New isolated directory; full logs remain local')
    p.add_argument('--timeout', type=int, default=300, choices=range(1, 301), metavar='1..300')
    args = p.parse_args()
    goose = shutil.which('goose')
    if goose is None:
        p.error('Existing Goose executable not found; no installation attempted')
    details = api('show', {'model': args.model})
    installed = validate_model(api('tags'), args.model, args.digest, details)
    if api('ps').get('models'):
        p.error('A model is already loaded; reserve the Ollama resource and resolve ownership first')
    args.output.mkdir(parents=True, exist_ok=False)
    task = args.task.read_bytes()
    isolated_task = args.output / 'task.txt'
    isolated_task.write_bytes(task)
    cmd = [goose, 'run', '--provider', 'ollama', '--model', args.model,
           '--no-profile', '--no-session', '--max-turns', '1', '--max-tool-repetitions', '1',
           '--stats', '--output-format', 'json', '--instructions', str(isolated_task.resolve())]
    env = os.environ.copy()
    env['OLLAMA_HOST'] = 'http://127.0.0.1:11434'
    report = {'provider': 'ollama', 'endpoint': ENDPOINT, 'model': args.model, 'digest': args.digest,
              'installed_size_bytes': installed.get('size'), 'details': details.get('details'),
              'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'goose_version': subprocess.check_output([goose, '--version'], text=True).strip(),
              'ollama_version': api('version'), 'task_sha256': hashlib.sha256(task).hexdigest(),
              'maximum_turns': 1, 'timeout_seconds': args.timeout, 'samples': [],
              'tokens': 'unavailable until verified in Goose output; no savings claim',
              'status': 'starting', 'inference_verified': False}
    start = time.monotonic()
    process = None
    try:
        with (args.output / 'goose-output.jsonl').open('wb') as stream:
            process = subprocess.Popen(cmd, cwd=args.output, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            while process.poll() is None:
                if time.monotonic() - start >= args.timeout:
                    report['status'] = 'timeout'
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    break
                active = [m for m in api('ps').get('models', []) if m.get('digest') == args.digest]
                runners = local_runners()
                if active and runners:
                    report['samples'].append({'seconds': round(time.monotonic() - start, 2),
                                              'loaded_model': active, 'local_runners': runners})
                    if any(r['model_blob_exists'] and r['model_blob_bytes'] > 0 for r in runners):
                        report['inference_verified'] = True
                time.sleep(2)
            report['returncode'] = process.returncode
            if report['status'] != 'timeout':
                report['status'] = 'completed_pending_review' if process.returncode == 0 else 'failed'
    except Exception as error:
        report['status'] = 'monitor_error'
        report['error'] = str(error)
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    finally:
        report['wall_seconds'] = round(time.monotonic() - start, 3)
        # The initial empty-model check prevents unloading a pre-existing user's model.
        try:
            api('generate', {'model': args.model, 'keep_alive': 0})
            report['loaded_models_after'] = api('ps').get('models', [])
        except Exception as error:
            report['unload_error'] = str(error)
        (args.output / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'inference_verified', 'wall_seconds')}))
    return 0 if report['status'] == 'completed_pending_review' and report['inference_verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
