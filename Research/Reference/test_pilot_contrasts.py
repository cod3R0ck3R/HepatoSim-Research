"""Synthetic arithmetic fixtures; no biological or simulation observations."""
import copy
import unittest

from analyze_benchmark import condition_contrasts


class PilotContrastTests(unittest.TestCase):
    def setUp(self):
        self.conditions = [
            {'id': name, 'model_file': name + '.ka', 'status': 'complete', 'runs': [
                {'seed': seed, 'samples': {'240': {'collagen_fold': 1 + factor * (seed - 100)}}}
                for seed in (101, 102, 103)]}
            for name, factor in [('control', 0), ('contrast', 1)]]

    def test_explicit_three_seed_pilot_computes_all_declared_pairs(self):
        result = condition_contrasts(self.conditions, [240], [101, 102, 103])[0]
        self.assertEqual(result['status'], 'descriptive_only')
        summary = result['by_day']['240']
        self.assertEqual([v['alternative_minus_reference_fold'] for v in summary['per_seed']], [1, 2, 3])
        self.assertEqual(summary['paired_difference']['mean'], 2)
        self.assertEqual(summary['paired_difference']['sd'], 1)

    def test_legacy_default_still_requires_five_prespecified_seeds(self):
        result = condition_contrasts(self.conditions, [240])[0]
        self.assertEqual(result['status'], 'withheld')
        self.assertEqual(result['seeds'], [101, 102, 103, 104, 105])

    def test_missing_and_incomplete_conditions_never_select_survivors(self):
        for condition in (0, 1):
            value = copy.deepcopy(self.conditions)
            value[condition]['status'] = 'incomplete'
            self.assertEqual(condition_contrasts(value, [240], [101, 102, 103])[0]['status'], 'withheld')
        value = copy.deepcopy(self.conditions)
        value[1]['runs'].pop()
        self.assertEqual(condition_contrasts(value, [240], [101, 102, 103])[0]['status'], 'withheld')


if __name__ == '__main__':
    unittest.main()
