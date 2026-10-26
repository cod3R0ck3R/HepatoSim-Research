"""Verify exported results and reproduce analyses in a disposable local copy."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from run import (specification, accepted_record, trace_hash_matches, extended_trace,
                 validate, digest, write_json)

HERE = Path(__file__).resolve().parent
spec = specification()
records = []
for job in spec['jobs']:
    folder = HERE/'results'/job['id']
    record = accepted_record(folder)
    assert record['status'] == 'completed'
    assert record['spec_sha256'] == digest(HERE/'spec.json')
    assert record['model_sha256'] == spec['models'][job['model']]
    assert record['runtime_sha256'] == spec['runtime']['executable_sha256']
    assert record.get('format_revalidated') or record['runner_sha256'] == digest(HERE/'run.py')
    assert trace_hash_matches(folder/'trace.csv',record['trace_sha256'])
    rows = extended_trace(folder/'trace.csv')
    assert rows[0]['[T]'] == 0
    validate(rows,job)
    records.append(record)
summary = json.loads((HERE/'results/analysis.json').read_text())
assert summary['three_seed_condition_complete']
assert summary['technical_checks']['seed_replay_exact']
for name in ['instrumentation','observation_grid',*[f'preintervention-{s}' for s in spec['primary_seeds']]]:
    assert summary['technical_checks'][name]['maximum_absolute_difference'] <= 1e-8
wall = sum(r['wall_seconds'] for r in records)
assert wall <= spec['budget']['total_new_run_seconds']
targets = ['results/analysis.json','results/conditional-grid.csv','identifiability-result.json']
with tempfile.TemporaryDirectory(prefix='hepatosim-fate-check-') as td:
    target = Path(td)/'check'
    shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__','*.log','verification.json'))
    for command in [[sys.executable,'-B','run.py','--analyze'],[sys.executable,'-B','identifiability.py']]:
        subprocess.run(command,cwd=target,check=True,stdout=subprocess.DEVNULL,timeout=20)
    for name in targets:
        assert (HERE/name).read_bytes() == (target/name).read_bytes(), name
    tests = subprocess.run([sys.executable,'-B','-m','unittest','-v','test_fate'],cwd=target,
                           capture_output=True,text=True,timeout=20)
    assert tests.returncode == 0,tests.stderr
    count = int(re.search(r'Ran (\d+) tests',tests.stderr).group(1))
receipt = {'tests_passed':count,'completed_KaSim_runs':len(records),'new_KaSim_wall_seconds':wall,
           'numeric_seed_replay_exact':True,'grid_and_history_checks_passed':True,
           'separate_process_analysis_byte_identical':True,'source_integrity_passed':True,
           'format_failure_preserved_and_revalidated':True,'independent_biological_validation':False,
           'artifact_sha256':{name:digest(HERE/name) for name in targets},
           'runner_sha256':digest(HERE/'run.py'),'verifier_sha256':digest(__file__)}
destination=HERE/'verification.json'
if destination.exists():
    assert json.loads(destination.read_text()) == receipt,'Existing verification differs; do not replace'
else:
    write_json(destination,receipt)
print(json.dumps(receipt,indent=2))
