import itertools
import math
from pathlib import Path
import tempfile
import unittest

from analyze_expression import calculate, matrix_rows, validate_inputs


class ExpressionTests(unittest.TestCase):
    def test_separation_and_complement_symmetry(self):
        result = calculate([[0, .1, .2, 2, 2.1, 2.2], [1, 1.1, 1.2, 3, 3.1, 3.2]])
        self.assertEqual(result['total_allocations'], 20)
        self.assertAlmostEqual(result['pseudo_f'], 600.0)
        self.assertEqual(result['exact_permutation_upper_tail_p'], .1)
        scores = {tuple(p['group_24h_indices']): p['pseudo_f'] for p in result['permutations']}
        for group, score in scores.items():
            self.assertAlmostEqual(score, scores[tuple(i for i in range(6) if i not in group)])

    def test_null_and_translation_invariance(self):
        self.assertEqual(calculate([[1] * 6, [2] * 6])['exact_permutation_upper_tail_p'], 1)
        rows = [[1, 2, 3, 5, 8, 9], [2, 3, 4, 6, 7, 8]]
        original = calculate(rows)
        shifted = calculate([[v + 100 for v in row] for row in rows])
        swapped = calculate([row[3:] + row[:3] for row in rows])
        self.assertAlmostEqual(original['pseudo_f'], shifted['pseudo_f'])
        self.assertAlmostEqual(original['pseudo_f'], swapped['pseudo_f'])
        self.assertEqual(original['exact_permutation_upper_tail_p'], swapped['exact_permutation_upper_tail_p'])

    def test_hand_computed_distance_and_effects(self):
        result = calculate([[0, 0, 0, 2, 2, 2], [2, 2, 2, 0, 0, 0]])
        self.assertEqual(result['pairwise_rms_log2'][0][3], 2)
        self.assertEqual(result['probe_sets_delta_at_least_1'], 1)
        self.assertEqual(result['probe_sets_delta_at_most_minus_1'], 1)
        self.assertTrue(all(r['sign_concordant'] == 2 for r in result['leave_one_per_group_out']))

    def test_bad_matrix_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'matrix.tsv'
            header = 'Hybridization REF\t' + '\t'.join('abcdef') + '\nComposite Element REF' + '\tRMA' * 6 + '\n'
            for data in ['x' + '\t1' * 6 + '\nx' + '\t2' * 6, 'x\tnan' + '\t1' * 5, 'x\t1\t2']:
                path.write_text(header + data)
                with self.assertRaises(ValueError):
                    list(matrix_rows(path, list('abcdef')))

    def test_hash_mismatch_stops_before_reading_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'input').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                validate_inputs(Path(tmp), {'inputs': {'input': {'sha256': 'wrong'}}})


if __name__ == '__main__':
    unittest.main()
