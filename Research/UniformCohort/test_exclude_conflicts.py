import copy
import unittest
from exclude_conflicts import exclude


class ExclusionTests(unittest.TestCase):
    def setUp(self):
        self.original = {'donor_cluster_values':[{'donor':d,'cluster':c,'condition':g,'genes':{'X':7}} for d,g in [('a','NORMAL'),('b','NASH'),('c','NAFL')] for c in [3,11]]}
        self.spec = {'exclude_donors':['c'],'expected_original_donors':3,'expected_retained_donors':2,'expected_groups':{'NORMAL':1,'NASH':1}}

    def test_excludes_entire_donor_preserves_original_and_counts(self):
        before=copy.deepcopy(self.original);new=exclude(self.original,self.spec)
        self.assertEqual(self.original,before)
        self.assertEqual(new['donor_cluster_values'],before['donor_cluster_values'][:4])
        new['donor_cluster_values'][0]['genes']['X']=99
        self.assertEqual(self.original,before)

    def test_missing_duplicate_or_unexpected_donors_rejected(self):
        for ids in [['missing'],['c','c'],['a']]:
            with self.subTest(ids=ids),self.assertRaises(ValueError):
                exclude(self.original,{**self.spec,'exclude_donors':ids})

    def test_duplicate_cluster_and_mixed_condition_rejected(self):
        bad=copy.deepcopy(self.original);bad['donor_cluster_values'].append(bad['donor_cluster_values'][0])
        with self.assertRaises(ValueError):exclude(bad,self.spec)
        bad=copy.deepcopy(self.original);bad['donor_cluster_values'][0]['condition']='NAFL'
        with self.assertRaises(ValueError):exclude(bad,self.spec)


if __name__=='__main__':unittest.main()
