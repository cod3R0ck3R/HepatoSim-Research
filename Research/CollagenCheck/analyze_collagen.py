#!/usr/bin/env python3
"""Retrospective aggregate CPA check; no drug-effect or individual-animal model."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_data(path, expected_hash):
    if sha(path) != expected_hash:
        raise ValueError('Input hash differs from frozen specification')
    with path.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 4 or {r['group'] for r in rows} != {'C-', 'C+', 'R1', 'R2'}:
        raise ValueError('Expected four distinct sacrifice groups')
    groups = {}
    for row in rows:
        group = row['group']
        if (row['study'] != 'Hofer2025' or row['toxin'] != 'CCl4' or
                row['unit'] != 'percent_collagen_proportionate_area' or
                row['statistic'] != 'median_and_IQR'):
            raise ValueError('Wrong study, toxin, units or statistic')
        expected_day = {'C-': '', 'C+': '0', 'R1': '7', 'R2': '14'}[group]
        expected_n = {'C-': 5, 'C+': 6, 'R1': 7, 'R2': 7}[group]
        if row['days_after_withdrawal'] != expected_day or int(row['n_animals']) != expected_n:
            raise ValueError('Unexpected time or sample size')
        q1, median, q3 = [float(row[k + '_cpa_percent']) for k in ('q1', 'median', 'q3')]
        if not all(math.isfinite(v) for v in (q1, median, q3)) or not 0 <= q1 <= median <= q3 <= 100:
            raise ValueError('Nonfinite or invalid CPA quartiles')
        groups[group] = (q1, median, q3)
    return groups


def rate(c0, c7, h):
    if not all(math.isfinite(x) for x in (c0, c7, h)) or not 0 <= h < c7 < c0 <= 100:
        raise ValueError('Expected declining positive excess CPA')
    return math.log((c0 - h) / (c7 - h)) / 7


def predict(c0, h, r, day):
    return h + (c0 - h) * math.exp(-r * day)


def analyze(groups, spec):
    h, c0, c7, c14 = [groups[g][1] for g in ('C-', 'C+', 'R1', 'R2')]
    r = rate(c0, c7, h)
    day = spec['check_day']
    predictions = {
        'healthy_offset_exponential': predict(c0, h, r, day),
        'zero_offset_exponential': predict(c0, 0, rate(c0, c7, 0), day),
        'constant': c0,
        'linear': c0 + (c7 - c0) * day / 7,
    }
    comparisons = {}
    for name, value in predictions.items():
        error = value - c14
        comparisons[name] = {'prediction_cpa_percent': value, 'signed_error_percentage_points': error,
                             'absolute_error_percentage_points': abs(error),
                             'relative_absolute_error': abs(error) / c14}
    grid = [(hh, aa, bb) for hh, aa, bb in itertools.product(groups['C-'], groups['C+'], groups['R1'])]
    rates = [rate(aa, bb, hh) for hh, aa, bb in grid]
    endpoints = [predict(aa, hh, rr, day) for (hh, aa, bb), rr in zip(grid, rates)]
    ambiguity = []
    for ratio in spec['q_over_r_illustrations']:
        q = ratio * r
        clearance = r + q
        changed_net_rate = (1 + spec['clearance_fraction_illustration']) * clearance - q
        ambiguity.append({'q_over_r': ratio, 'production_coefficient_per_day': q,
                          'clearance_coefficient_per_day': clearance,
                          'baseline_net_rate_per_day': clearance - q,
                          'perturbed_prediction_cpa_percent': predict(c0, h, changed_net_rate, day)})
    return {'specification': spec['id'], 'scope': spec['role'],
            'net_decline_rate_per_day': r, 'net_excess_half_time_days': math.log(2) / r,
            'comparisons': comparisons,
            'primary_beats_constant': abs(predictions['healthy_offset_exponential'] - c14) < abs(c0 - c14),
            'sensitivity': {'combinations': len(grid), 'net_rate_min_max_per_day': [min(rates), max(rates)],
                            'prediction_min_max_cpa_percent': [min(endpoints), max(endpoints)],
                            'interpretation': 'IQR corner sensitivity only; not CI or parameter probability'},
            'structural_counterexamples': ambiguity,
            'mechanism_conclusion': 'Production and clearance are structurally non-identifiable from net CPA alone; illustration coefficients are arbitrary, not biologically calibrated.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    expected_spec_hash = args.spec.with_suffix('.sha256').read_text().split()[0]
    if sha(args.spec) != expected_spec_hash:
        raise ValueError('Frozen specification hash mismatch')
    spec = json.loads(args.spec.read_text())
    result = analyze(load_data(args.input, spec['input_sha256']), spec)
    result['provenance'] = {'input_sha256': sha(args.input), 'spec_sha256': sha(args.spec),
                            'analysis_sha256': sha(Path(__file__))}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    (args.output / 'environment.json').write_text(json.dumps({'python': sys.version, 'system': platform.system(),
        'release': platform.release(), 'machine': platform.machine(), 'solver': 'analytic closed form; no ODE integration or randomness'}, indent=2) + '\n')
    (args.output / 'SHA256SUMS').write_text(''.join(sha(args.output / f) + '  ' + f + '\n' for f in ('result.json', 'environment.json')))
    print(json.dumps({'status': 'completed', 'result_sha256': sha(args.output / 'result.json')}))


if __name__ == '__main__':
    main()
