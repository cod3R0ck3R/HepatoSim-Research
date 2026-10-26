"""Verify immutable results, exact endpoint arithmetic and a fresh-process replay."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from check import spec, digest, read_trace, rows_for, validate, extended_trace, common_error, write_json

HERE = Path(__file__).resolve().parent
s = spec()
amendment = json.loads((HERE/'export-amendment.json').read_text())
assert digest(HERE/'executed-check.py') == amendment['executed_runner_sha256']
assert digest(HERE/'check.py') == amendment['public_adapter_sha256']
assert not amendment['scientific_model_or_criteria_changed']
result = json.loads((HERE/'results/analysis.json').read_text())
provenance = json.loads((HERE/'analysis-provenance.json').read_text())
assert provenance['raw_trace_analysis_sha256'] == digest(HERE/'results/analysis.json')
assert provenance['checker_sha256'] == digest(HERE/'check.py')
assert result['all_new_jobs_complete'] and result['new_run_count'] == 11
assert result['new_run_wall_seconds'] <= s['budget']['total_new_run_seconds']
assert not result['biological_validation'] and not result['drug_parameter_mapping']
for seed in range(101,111):
    control = read_trace(HERE/f'archive/control-{seed}.trace.csv')
    assert any(r['[T]'] == 90 for r in control)
    if seed <= 103:
        old = read_trace(HERE.parent/f'HSCFate/archive/control-{seed}.csv')
        comparison = common_error(control,old)
        assert comparison['shared_times'] >= 197 and comparison['maximum_absolute_difference'] == 0
        trace = extended_trace(HERE.parent/f'HSCFate/results/fate50-{seed}/trace.csv')
    else:
        trace = rows_for(HERE/f'results/fate50-{seed}/trace.csv')
    validate(trace,{'model':'fate50','fate_after':.5},control)
    a = next(r for r in reversed(control) if r['[T]'] == 90)
    b = next(r for r in reversed(trace) if r['[T]'] == 90)
    for key in s['observables']:
        record = next(d for d in result['differences'] if d['seed'] == seed and d['observable'] == key)
        assert record['control'] == a[key] and record['scenario'] == b[key]
        assert record['difference'] == b[key]-a[key]

with tempfile.TemporaryDirectory(prefix='hepatosim-robust-check-') as td:
    target = Path(td)
    for name in ['HSCRobustness','HSCFate']:
        shutil.copytree(HERE.parent/name,target/name,ignore=shutil.ignore_patterns('__pycache__','*.log','verification.json'))
    subprocess.run([sys.executable,'-B','check.py','--analyze'],cwd=target/'HSCRobustness',check=True,stdout=subprocess.DEVNULL,timeout=30)
    assert (HERE/'results/analysis.json').read_bytes() == (target/'HSCRobustness/results/analysis.json').read_bytes()
    tests = subprocess.run([sys.executable,'-B','-m','unittest','-v','test_check'],cwd=target/'HSCRobustness',capture_output=True,text=True,timeout=30)
    assert tests.returncode == 0,tests.stderr
    count = int(re.search(r'Ran (\d+) tests',tests.stderr).group(1))
receipt = {'tests_passed':count,'completed_new_KaSim_runs':11,'new_run_wall_seconds':result['new_run_wall_seconds'],
           'paired_seeds':10,'alternative_assumption_pairs':2,'complete_half_day_grid':True,
           'old_control_and_pilot_history_exact':True,'endpoint_arithmetic_exact':True,
           'separate_process_analysis_byte_identical':True,'source_integrity_passed':True,
           'raw_and_public_analysis_byte_identical':True,'failed_manifests_preserved':provenance['failed_manifests_preserved'],
           'runner_sha256':digest(HERE/'check.py'),'executed_runner_sha256':digest(HERE/'executed-check.py'),
           'verifier_sha256':digest(__file__),'analysis_sha256':digest(HERE/'results/analysis.json'),
           'biological_validation':False,'laboratory_forwarding':False}
destination = HERE/'verification.json'
if destination.exists():
    assert json.loads(destination.read_text()) == receipt, 'Existing verification differs; preserve it'
else:
    write_json(destination,receipt)
print(json.dumps(receipt,indent=2))
