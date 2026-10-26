"""Exploratory feasibility of one positive scaling divisor per graph group."""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import platform
import analyze


def compatible(b, c, b_rounding, c_rounding):
    values = list(b) + list(c) + [b_rounding, c_rounding]
    if any(not math.isfinite(x) for x in values):
        raise ValueError('Finite numeric inputs required')
    if len(b) != len(c) or len(b) < 2 or min(b_rounding, c_rounding) < 0:
        raise ValueError('Equal groups with at least two points and nonnegative rounding required')
    rb, rc = map(lambda x: Fraction(str(x)), [b_rounding, c_rounding])
    pairs = zip(sorted(map(lambda x: Fraction(str(x)), b)), sorted(map(lambda x: Fraction(str(x)), c)))
    intervals = []
    for x, y in pairs:
        if x <= rb or y <= rc:
            raise ValueError('Rounding intervals must remain positive')
        intervals.append(((x-rb)/(y+rc), (x+rb)/(y-rc)))
    lower = max(x[0] for x in intervals)
    upper = min(x[1] for x in intervals)
    return {'n': len(b), 'compatible_with_one_divisor': lower <= upper,
            'required_divisor_lower_bound': float(lower), 'required_divisor_upper_bound': float(upper),
            'empty_interval_gap': float(max(Fraction(0), lower-upper))}


def run(workbook, spec_path):
    spec = json.loads(Path(spec_path).read_text())
    if analyze.sha(workbook) != spec['source_sha256']:
        raise ValueError('Source hash differs from frozen protocol')
    b, c = [analyze.extract(analyze.worksheet(workbook, name)) for name in ['Fig. 2B', 'Fig. 2C']]
    groups = [{'group': name, **compatible(x, y, spec['B_rounding_percent_points'], spec['C_rounding_dimensionless'])}
              for name, x, y in zip(analyze.GROUPS, b, c)]
    return {'spec_id': spec['id'], 'spec_sha256': analyze.sha(spec_path), 'source_sha256': analyze.sha(workbook),
            'code_sha256': analyze.sha(__file__), 'extractor_sha256': analyze.sha(analyze.__file__),
            'python': platform.python_version(), 'groups': groups,
            'all_groups_compatible': all(g['compatible_with_one_divisor'] for g in groups),
            'status': 'exploratory_source_consistency_check', 'calibration_performed': False,
            'independent_biological_validation': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['workbook', 'spec', 'output']:
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args()
    result = run(args.workbook, args.spec)
    with args.output.open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'groups': result['groups'], 'all_groups_compatible': result['all_groups_compatible']}))
