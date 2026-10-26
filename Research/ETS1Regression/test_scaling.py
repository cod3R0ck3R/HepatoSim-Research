import unittest
from check_scaling import compatible


class ScalingTests(unittest.TestCase):
    def test_known_divisor_and_reordered_rows(self):
        r = compatible([2, 4, 6], [3, 1, 2], 0, 0)
        self.assertTrue(r['compatible_with_one_divisor'])
        self.assertEqual(r['required_divisor_lower_bound'], 2)
        self.assertEqual(r['required_divisor_upper_bound'], 2)

    def test_no_divisor_even_when_means_can_be_normalized(self):
        r = compatible([2, 4], [1, 1], .005, .000005)
        self.assertFalse(r['compatible_with_one_divisor'])
        self.assertGreater(r['empty_interval_gap'], 1.9)

    def test_rounding_feasible_without_changing_observations(self):
        self.assertTrue(compatible([1.99, 4.01], [1, 2], .01, 0)['compatible_with_one_divisor'])
        self.assertFalse(compatible([1.99, 4.01], [1, 2], 0, 0)['compatible_with_one_divisor'])

    def test_invalid_data_rejected(self):
        for args in [([1, 2], [1], 0, 0), ([1, 2], [1, 2], -1, 0),
                     ([0, 2], [1, 2], 0, 0), ([1, float('nan')], [1, 2], 0, 0),
                     ([1, 2], [1, 2], 0, 1), ([1, 2], [1, 2], float('inf'), 0)]:
            with self.assertRaises(ValueError): compatible(*args)

if __name__ == '__main__': unittest.main()
