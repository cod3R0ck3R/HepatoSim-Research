"""Internal cross-toxin transfer check; CPA is an area fraction, not collagen mass."""
import argparse
import csv
import itertools
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'CollagenCheck'))
from analyze_collagen import load_data, rate, predict, sha


def load_taa(path, expected_hash):
    if sha(path) != expected_hash:
        raise ValueError('TAA input hash mismatch')
    rows = list(csv.DictReader(path.open()))
    if len(rows) != 4 or [r['group'] for r in rows] != ['C-', 'C+', 'R1', 'R2']:
        raise ValueError('TAA groups mismatch')
    result = {}
    for row, day in zip(rows, ['', '0', '7', '14']):
        if (row['toxin'] != 'TAA' or row['study'] != 'Hofer2025' or
                row['statistic'] != 'median_and_IQR' or
                row['unit'] != 'percent_collagen_proportionate_area' or
                int(row['n_animals']) != 8 or row['days_after_withdrawal'] != day):
            raise ValueError('TAA provenance mismatch')
        values = tuple(float(row[k + '_cpa_percent']) for k in ['q1', 'median', 'q3'])
        if not all(math.isfinite(x) for x in values) or not 0 <= values[0] <= values[1] <= values[2] <= 100:
            raise ValueError('Invalid TAA quartiles')
        result[row['group']] = values
    return result


def analyze(source, target):
    sh, s0, s7 = [source[g][1] for g in ['C-', 'C+', 'R1']]
    h, c0, c7, c14 = [target[g][1] for g in ['C-', 'C+', 'R1', 'R2']]
    r = rate(s0, s7, sh)
    tr = rate(c0, c7, h)
    methods = {'fixed_ccl4_transfer': lambda t: predict(c0, h, r, t),
               'constant': lambda t: c0,
               'taa_day0_day7_fit': lambda t: predict(c0, h, tr, t),
               'zero_offset_ccl4_transfer': lambda t: predict(c0, 0, rate(s0, s7, 0), t)}
    comparisons = {}
    for name, fun in methods.items():
        rows = []
        for day, observed in [(7, c7), (14, c14)]:
            value = fun(day); error = value - observed
            rows.append({'day': day, 'prediction_cpa_percent': value,
                         'signed_error_percentage_points': error,
                         'absolute_error_percentage_points': abs(error)})
        comparisons[name] = {'endpoints': rows,
                            'mae_percentage_points': sum(row['absolute_error_percentage_points'] for row in rows)/2}
    corners = []
    for hh, aa, bb, th, tc0 in itertools.product(source['C-'], source['C+'], source['R1'], target['C-'], target['C+']):
        corners.append(predict(tc0, th, rate(aa, bb, hh), 14))
    return {'scope': 'retrospective same-study transfer check; all aggregate values previously seen',
            'ccl4_rate_per_day': r, 'taa_descriptive_rate_per_day': tr,
            'comparisons': comparisons,
            'primary_beats_constant_day14': comparisons['fixed_ccl4_transfer']['endpoints'][1]['absolute_error_percentage_points'] < comparisons['constant']['endpoints'][1]['absolute_error_percentage_points'],
            'sensitivity': {'combinations': len(corners), 'day14_prediction_min_max': [min(corners), max(corners)],
                            'interpretation': 'quartile-corner sensitivity; not confidence or credible interval'},
            'independent_biological_validation': False, 'drug_effect_identified': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['ccl4', 'taa', 'spec', 'output']:
        p.add_argument('--'+name, required=True, type=Path)
    a = p.parse_args()
    if sha(a.spec) != a.spec.with_suffix('.sha256').read_text().split()[0]:
        raise ValueError('Specification hash mismatch')
    spec = json.loads(a.spec.read_text())
    result = analyze(load_data(a.ccl4, spec['ccl4_sha256']), load_taa(a.taa, spec['taa_sha256']))
    result['provenance'] = {'spec_sha256': sha(a.spec), 'code_sha256': sha(Path(__file__)),
                            'helper_sha256': sha(Path(__file__).resolve().parents[1]/'CollagenCheck/analyze_collagen.py'),
                            'ccl4_sha256': sha(a.ccl4), 'taa_sha256': sha(a.taa)}
    with a.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
