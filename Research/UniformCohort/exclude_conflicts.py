#!/usr/bin/env python3
"""Frozen post hoc sensitivity excluding whole donors with conflicting labels."""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import platform
import signal
import compartments


def exclude(result, spec):
    out = copy.deepcopy(result)
    rows = out['donor_cluster_values']
    donors = {r['donor'] for r in rows}
    removed = set(spec['exclude_donors'])
    if len(removed) != len(spec['exclude_donors']) or not removed <= donors:
        raise ValueError('Missing or duplicate exclusion donor')
    if len(donors) != spec['expected_original_donors']:
        raise ValueError('Unexpected source donor count')
    keys = [(r['donor'], r['cluster']) for r in rows]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate donor/cluster row')
    groups = {}
    for r in rows:
        if r['donor'] in groups and groups[r['donor']] != r['condition']:
            raise ValueError('Inconsistent donor condition')
        groups[r['donor']] = r['condition']
    remaining = {d:g for d,g in groups.items() if d not in removed}
    if len(remaining) != spec['expected_retained_donors'] or dict(Counter(remaining.values())) != spec['expected_groups']:
        raise ValueError('Unexpected retained groups')
    out['donor_cluster_values'] = [r for r in rows if r['donor'] not in removed]
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['result','spec','compartment-spec','output']:
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args(); spec = json.loads(a.spec.read_text()); shared = compartments.analyze.shared
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('Budget expired')))
    signal.alarm(spec['budget']['wall_seconds'])
    if shared.sha(a.result) != spec['input_result_sha256'] or shared.sha(a.compartment_spec) != spec['compartment_spec_sha256']:
        raise ValueError('Frozen input hash mismatch')
    original = json.loads(a.result.read_text())
    if original['binding']['code_sha256'] != shared.sha(compartments.analyze.__file__) or original['binding']['parser_sha256'] != shared.sha(shared.__file__):
        raise ValueError('Prior aggregation code mismatch')
    out = compartments.summarize(exclude(original,spec),json.loads(a.compartment_spec.read_text()))
    out.update(analysis_role=spec['status'], excluded_donors=spec['exclude_donors'], retained_groups=spec['expected_groups'])
    out['binding'] = {k:shared.sha(v) for k,v in {'input_result_sha256':a.result,'spec_sha256':a.spec,'compartment_spec_sha256':a.compartment_spec,'code_sha256':Path(__file__),'compartment_code_sha256':Path(compartments.__file__),'statistics_code_sha256':Path(compartments.analyze.__file__),'parser_sha256':Path(shared.__file__)}.items()}
    out['binding'].update(python=platform.python_version(),numpy=compartments.np.__version__)
    shared.write_new(a.output,out)
    print(json.dumps({'tests':out['tests'],'joint_direction_rule_met':out['joint_direction_rule_met'],'sha256':shared.sha(a.output)}))


if __name__ == '__main__':
    main()
