#!/usr/bin/env python3
"""HSR-EXPR-001: deterministic exploratory statistics, using Python's standard library."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import signal
import sys


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_inputs(folder, spec):
    for name, entry in spec['inputs'].items():
        if Path(name).name != name or sha(folder / name) != entry['sha256']:
            raise ValueError('Input name or checksum mismatch: ' + name)
    with (folder / 'E-MEXP-3177.sdrf.txt').open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    samples = [r['Hybridization Name'] for r in rows]
    times = [int(r['Factor Value[TIME]']) for r in rows]
    if samples != spec['sample_names'] or times != spec['group_hours']:
        raise ValueError('SDRF sample/group order mismatch')
    if any(r['Characteristics[Organism]'] != 'Mus musculus' or
           r['Characteristics[CellType]'] != 'macrophage' for r in rows):
        raise ValueError('Unexpected biological system')


def matrix_rows(path, names):
    with path.open() as stream:
        reader = csv.reader(stream, delimiter='\t')
        if next(reader, []) != ['Hybridization REF', *names]:
            raise ValueError('Matrix sample columns mismatch')
        if next(reader, []) != ['Composite Element REF', *(['RMA'] * 6)]:
            raise ValueError('Expected author-normalized RMA matrix')
        seen = set()
        for row in reader:
            if len(row) != 7 or not row[0] or row[0] in seen:
                raise ValueError('Malformed or duplicate probe set')
            seen.add(row[0])
            values = [float(x) for x in row[1:]]
            if not all(math.isfinite(x) for x in values):
                raise ValueError('Nonfinite intensity')
            yield values


def pseudo_f(gram, group):
    other = [i for i in range(6) if i not in group]
    total = math.fsum(gram[i][i] for i in range(6))
    between = math.fsum(math.fsum(gram[i][j] for i in g for j in g) / 3
                        for g in (group, other))
    within = max(0.0, total - between)
    if within == 0:
        return math.inf if between > 0 else 0.0
    return max(0.0, between) / (within / 4)


def quantile(values, probability):
    position = (len(values) - 1) * probability
    low = int(position)
    high = math.ceil(position)
    return values[low] + (values[high] - values[low]) * (position - low)


def calculate(rows):
    gram = [[0.0] * 6 for _ in range(6)]
    sums, squares = [0.0] * 6, [0.0] * 6
    effects = []
    subsets = list(itertools.product(range(3), range(3, 6)))
    stable_sign, stable_threshold = [0] * 9, [0] * 9
    up = down = 0
    for values in rows:
        if len(values) != 6 or not all(math.isfinite(v) for v in values):
            raise ValueError('Six finite values required')
        center = math.fsum(values) / 6
        centered = [v - center for v in values]
        for i in range(6):
            sums[i] += values[i]
            squares[i] += values[i] ** 2
            for j in range(i, 6):
                gram[i][j] += centered[i] * centered[j]
        delta = math.fsum(values[3:]) / 3 - math.fsum(values[:3]) / 3
        effects.append(delta)
        if abs(delta) >= 1:
            up += delta > 0
            down += delta < 0
            for k, (a, b) in enumerate(subsets):
                contrast = (math.fsum(values[j] for j in range(3, 6) if j != b) -
                            math.fsum(values[j] for j in range(3) if j != a)) / 2
                stable_sign[k] += contrast * delta > 0
                stable_threshold[k] += abs(contrast) >= 1
    count = len(effects)
    if count < 2:
        raise ValueError('At least two probe sets required')
    for i in range(6):
        for j in range(i):
            gram[i][j] = gram[j][i]
    permutations = [{'group_24h_indices': list(g), 'pseudo_f': pseudo_f(gram, g)}
                    for g in itertools.combinations(range(6), 3)]
    observed = permutations[0]['pseudo_f']
    tolerance = 1e-10 * max(1.0, observed) if math.isfinite(observed) else 0
    extreme = sum(p['pseudo_f'] >= observed - tolerance for p in permutations)
    rms = [[math.sqrt(max(0, gram[i][i] + gram[j][j] - 2 * gram[i][j]) / count)
            for j in range(6)] for i in range(6)]
    effects.sort()
    return {'probe_sets': count, 'samples': 6,
            'sample_means': [s / count for s in sums],
            'sample_sd_across_probe_sets': [math.sqrt(max(0, squares[i] - sums[i] ** 2 / count) / (count - 1)) for i in range(6)],
            'pairwise_rms_log2': rms, 'pseudo_f': observed,
            'exact_permutation_upper_tail_p': extreme / 20,
            'extreme_allocations': extreme, 'total_allocations': 20,
            'permutations': permutations,
            'mean_72_minus_24_quantiles': {str(q): quantile(effects, q) for q in (0, .05, .25, .5, .75, .95, 1)},
            'probe_sets_delta_at_least_1': up, 'probe_sets_delta_at_most_minus_1': down,
            'leave_one_per_group_out': [{'excluded_sample_indices': list(pair),
                                        'sign_concordant': stable_sign[k],
                                        'abs_delta_at_least_1': stable_threshold[k],
                                        'denominator': up + down} for k, pair in enumerate(subsets)]}


def write_outputs(folder, result, names):
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    with (folder / 'distances.csv').open('w') as stream:
        writer = csv.writer(stream); writer.writerow(['sample', *names])
        for name, row in zip(names, result['statistics']['pairwise_rms_log2']):
            writer.writerow([name, *row])
    with (folder / 'permutations.csv').open('w') as stream:
        writer = csv.writer(stream); writer.writerow(['24h_group_indices', 'pseudo_f'])
        for row in result['statistics']['permutations']:
            writer.writerow([' '.join(map(str, row['group_24h_indices'])), row['pseudo_f']])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--spec', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text())
    signal.signal(signal.SIGALRM, lambda *_: sys.exit('Analysis wall budget exceeded'))
    signal.alarm(spec['budget']['timeout_seconds_per_run'])
    validate_inputs(args.inputs, spec)
    statistics = calculate(matrix_rows(args.inputs / spec['matrix'], spec['sample_names']))
    if statistics['probe_sets'] != spec['expected_probe_sets']:
        raise ValueError('Unexpected number of probe sets')
    result = {'benchmark': spec['id'], 'specification_sha256': sha(args.spec),
              'analysis_code_sha256': sha(Path(__file__)), 'python': platform.python_version(),
              'inputs_sha256': {name: sha(args.inputs / name) for name in spec['inputs']},
              'scientific_status': 'exploratory_expression_reanalysis_not_independent_validation',
              'statistics': statistics}
    write_outputs(args.output, result, spec['sample_names'])
    print(json.dumps({'probe_sets': statistics['probe_sets'], 'pseudo_f': statistics['pseudo_f'],
                      'exact_p': statistics['exact_permutation_upper_tail_p'], 'result_sha256': sha(args.output / 'result.json')}))


if __name__ == '__main__':
    main()
