import unittest
from extract_decaris_collagen import extract

class Tests(unittest.TestCase):
    def test_units_columns_and_missingness(self):
        header='#003 #004 #005 #007 #009 #011\n'
        a=header+''.join(p+' 10 20 30 40 50 60 0.9\n' for p in ['P02452','P08123','P02461'])
        f=header+'Total fraction new\n'+''.join(p+' 1% 2% 3% 4% 5% 6%\n' for p in ['P02452','P08123','P02461'])
        k='Supplementary Table 2 Fractional synthesis rate - % new per day (k)\n'+''.join(p+' 0.1% 0.2% 0.3% 0.4% 0.5% 0.6% 0.9\n' for p in ['P02452','P08123','P02461'])
        r=extract(a,f+k)
        self.assertEqual(len(r),18)
        self.assertEqual(r[0]['fraction_new_percent_over_labeling_period'],1)
        self.assertEqual(r[0]['fractional_synthesis_percent_per_day'],0.1)
        with self.assertRaises(ValueError):extract(a,(f+k).replace('1% 2%','2%',1))
        with self.assertRaises(ValueError):extract(a.replace('#003','#004'),f+k)
