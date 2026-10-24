import unittest
import math
from analyze_transfer import analyze

class TransferTests(unittest.TestCase):
    def test_identical_synthetic_system_transfers_exactly(self):
        g={'C-':(1,1,1),'C+':(9,9,9),'R1':(5,5,5),'R2':(3,3,3)}
        r=analyze(g,g)
        self.assertAlmostEqual(r['comparisons']['fixed_ccl4_transfer']['mae_percentage_points'],0)
        self.assertEqual(r['sensitivity']['combinations'],243)

    def test_target_late_values_do_not_change_transfer(self):
        s={'C-':(1,1,1),'C+':(9,9,9),'R1':(5,5,5),'R2':(3,3,3)}
        t=dict(s);t['R1']=(7,7,7);t['R2']=(7,7,7)
        r=analyze(s,t)
        self.assertAlmostEqual(r['ccl4_rate_per_day'],math.log(2)/7)
        self.assertAlmostEqual(r['comparisons']['fixed_ccl4_transfer']['endpoints'][1]['prediction_cpa_percent'],3)
        self.assertFalse(r['independent_biological_validation'])
        self.assertFalse(r['primary_beats_constant_day14'])

if __name__ == '__main__': unittest.main()
