#!/usr/bin/env python3
"""Explicit post hoc provenance sensitivity; never silently replace source labels."""
import argparse
import copy
import json
from pathlib import Path
import compartments


def relabel(result,spec):
    out=copy.deepcopy(result);seen=set()
    for row in out['donor_cluster_values']:
        if row['donor'] in spec['conflicts']:
            c=spec['conflicts'][row['donor']]
            if row['condition']!=c['matrix_metadata']:raise ValueError('Unexpected original group')
            row['condition']=c['workbook'];seen.add(row['donor'])
    if seen!=set(spec['conflicts']):raise ValueError('Missing conflicting donors')
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['result','compartment-spec','spec','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();original=json.loads(a.result.read_text());spec=json.loads(a.spec.read_text())
    r=compartments.summarize(relabel(original,spec),json.loads(a.compartment_spec.read_text()))
    r['analysis_role']=spec['status'];r['binding']={n:compartments.analyze.shared.sha(v) for n,v in {'input_result_sha256':a.result,'spec_sha256':a.spec,'compartment_spec_sha256':a.compartment_spec,'code_sha256':Path(__file__),'compartment_code_sha256':Path(compartments.__file__)}.items()}
    compartments.analyze.shared.write_new(a.output,r);print(json.dumps({'tests':r['tests'],'joint_direction_rule_met':r['joint_direction_rule_met']}))

if __name__=='__main__':main()
