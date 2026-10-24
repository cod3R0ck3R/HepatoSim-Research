import io
import unittest
import numpy as np
from analyze import counts, bh, ranks, statistics


class Checks(unittest.TestCase):
    def test_counts_summary_excluded(self):
        total,v,n=counts(io.StringIO('ENSG1\t3\nENSG2\t7\n__no_feature\t100\n'),{'ENSG1'})
        self.assertEqual((total,v,n),(10,{'ENSG1':3},2))

    def test_bad_counts(self):
        for s in ['ENSG1\t-1\n','ENSG1\t1.5\n','ENSG1\t2\nENSG1\t3\n','ENSG2\t4\n']:
            with self.assertRaises(ValueError): counts(io.StringIO(s),{'ENSG1'})

    def test_bh_and_ties(self):
        np.testing.assert_allclose(bh([.01,.04,.03]),[.03,.04,.04])
        np.testing.assert_equal(ranks([5,1,1,9]),[3,1.5,1.5,4])

    def test_null_and_replay(self):
        a=np.array([1.,2.,3.]);b=a.copy()
        r=statistics(a,b,np.random.default_rng(7),99,100)
        self.assertEqual(r['p'],1.)
        self.assertEqual(r,statistics(a,b,np.random.default_rng(7),99,100))

    def test_direction_and_loo(self):
        r=statistics(np.array([5.,6.,7.]),np.array([1.,2.,3.]),np.random.default_rng(8),999,500)
        self.assertEqual(r['effect'],4.)
        self.assertEqual(r['leave_one_out_range'],[3.5,4.5])
        self.assertLess(r['p'],.15)
        self.assertGreater(r['ci95_unadjusted'][0],0)


if __name__=='__main__': unittest.main()
