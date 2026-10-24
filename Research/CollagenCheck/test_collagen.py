import csv
import math
from pathlib import Path
import tempfile
import unittest
from analyze_collagen import analyze, load_data, predict, rate, sha


class CollagenTests(unittest.TestCase):
    def test_analytic_fixture(self):
        r = rate(17, 9, 1)
        self.assertAlmostEqual(r, math.log(2) / 7)
        self.assertAlmostEqual(predict(17, 1, r, 14), 5)

    def test_invalid_decay(self):
        for values in [(1, 2, 0), (2, 1, 1), (float('nan'), 1, 0), (101, 5, 1)]:
            with self.assertRaises(ValueError): rate(*values)

    def test_structural_nonidentifiability(self):
        r = .1
        for q in (0, .1, .4, 2):
            for x in (0, 1, 20):
                self.assertAlmostEqual(q*x - (r+q)*x, -r*x)

    def test_internal_check_and_sensitivity(self):
        groups = {'C-': (.8, 1, 1.2), 'C+': (16, 17, 18), 'R1': (8, 9, 10), 'R2': (4, 5, 6)}
        spec = {'check_day': 14, 'q_over_r_illustrations': [0, 1, 4], 'clearance_fraction_illustration': .25,
                'id': 'synthetic-test', 'role': 'synthetic'}
        result = analyze(groups, spec)
        self.assertAlmostEqual(result['comparisons']['healthy_offset_exponential']['absolute_error_percentage_points'], 0)
        self.assertTrue(result['primary_beats_constant'])
        self.assertEqual(result['sensitivity']['combinations'], 27)
        points = [r['perturbed_prediction_cpa_percent'] for r in result['structural_counterexamples']]
        self.assertGreater(points[0], points[1]); self.assertGreater(points[1], points[2])

    def test_input_contract(self):
        fields = ['study','toxin','group','days_after_withdrawal','n_animals','median_cpa_percent','q1_cpa_percent','q3_cpa_percent','statistic','unit']
        rows = [['Hofer2025','CCl4',g,t,n,m,q1,q3,'median_and_IQR','percent_collagen_proportionate_area']
                for g,t,n,m,q1,q3 in [('C-','',5,1,.8,1.2),('C+','0',6,17,16,18),('R1','7',7,9,8,10),('R2','14',7,5,4,6)]]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'synthetic.csv'
            def write():
                with path.open('w',newline='') as f:
                    writer=csv.writer(f); writer.writerow(fields); writer.writerows(rows)
            write()
            self.assertEqual(len(load_data(path,sha(path))),4)
            with self.assertRaises(ValueError): load_data(path,'0'*64)
            rows[0][6] = 10; write()
            with self.assertRaises(ValueError): load_data(path,sha(path))
            rows[0][6] = .8; rows[1][1]='TAA'; write()
            with self.assertRaises(ValueError): load_data(path,sha(path))


if __name__ == '__main__':
    unittest.main()
