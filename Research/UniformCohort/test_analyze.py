import io
import unittest
import numpy as np
from analyze import aggregate,statistics,shared

class AuditTests(unittest.TestCase):
    def test_exact_permutation_and_seed(self):
        a=statistics([4,5,6],[1,2,3],np.random.default_rng(1),100)
        b=statistics([4,5,6],[1,2,3],np.random.default_rng(1),100)
        self.assertEqual(a,b);self.assertEqual(a['permutations'],20);self.assertAlmostEqual(a['exact_permutation_p'],.1)
        self.assertGreater(a['loo_min'],0)
    def test_asymmetric_groups_and_null(self):
        r=statistics([1]*9,[1]*5,np.random.default_rng(1),100)
        self.assertEqual(r['permutations'],2002);self.assertEqual(r['exact_permutation_p'],1)
        self.assertEqual(r['bootstrap95'],[0,0])
    def test_aggregation_and_oracles(self):
        spec={'dimensions':[2,2,3],'donors':{'a':'NORMAL','b':'MASH'},'clusters':[0],
              'targets':['X'],'markers':[],'budget':{'parser_max_nnz':300000000}}
        raw=b'%%MatrixMarket matrix coordinate integer general\n2 2 3\n1 1 2\n2 1 3\n1 2 4\n'
        r=aggregate(io.BytesIO(raw),spec,np.array([0,1]),np.array([5,4]),np.array([2,1]),np.array([0,-1]))
        self.assertEqual(r['gene_counts'],[[2],[4]]);self.assertEqual(r['total_counts'],[5,4])
        with self.assertRaises(ValueError):aggregate(io.BytesIO(raw),spec,np.array([0,1]),np.array([6,4]),np.array([2,1]),np.array([0,-1]))
    def test_parser_limit_opt_in(self):
        raw=b'%%MatrixMarket matrix coordinate integer general\n1 1 100000001\n'
        with self.assertRaisesRegex(ValueError,'capacity'):list(shared.coordinates(io.BytesIO(raw)))
        with self.assertRaisesRegex(ValueError,'Truncated'):list(shared.coordinates(io.BytesIO(raw),max_nnz=300000000))
        with self.assertRaisesRegex(ValueError,'capacity'):list(shared.coordinates(io.BytesIO(raw),max_nnz=300000001))
    def test_checkpoint_tamper(self):
        import tempfile,json
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text(json.dumps({'binding':{},'sample':{},'sample_sha256':'wrong'}))
            with self.assertRaises(ValueError):shared.read_checkpoint(p,{})



class MergeTests(unittest.TestCase):
    def test_merge_counts_before_normalization(self):
        from compartments import merge
        raw={'donor_cluster_values':[{'donor':'d','condition':'MASH','cluster':c,'nuclei':1,'total_UMI':den,'genes':{'X':{'UMI':v,'detected_nuclei':1}}} for c,den,v in [(3,10,2),(11,90,3)]]}
        row=merge(raw,{'compartments':{'HSC':[3,11]}})[0]
        self.assertEqual(row['genes']['X']['UMI'],5);self.assertEqual(row['total_UMI'],100)
        self.assertAlmostEqual(row['genes']['X']['log2cpm'],np.log2(50001))
        with self.assertRaises(ValueError):merge(raw,{'compartments':{'HSC':[3,12]}})

class SourceLabelTests(unittest.TestCase):
    def test_unknown_contrast_fails(self):
        from analyze import summarize
        spec={"donors":{"d":"NASH"},"clusters":[0],"targets":[],"markers":[],"contrast":["MASH","NORMAL"]}
        with self.assertRaisesRegex(ValueError,"Contrast labels"):summarize(spec,{})

class LabelTests(unittest.TestCase):
    def test_relabel_preserves_counts_and_original(self):
        from label_sensitivity import relabel
        old={"donor_cluster_values":[{"donor":"d","condition":"NASH","genes":{"X":2}}]}
        spec={"conflicts":{"d":{"matrix_metadata":"NASH","workbook":"NAFL"}}}
        new=relabel(old,spec)
        self.assertEqual(old["donor_cluster_values"][0]["condition"],"NASH")
        self.assertEqual(new["donor_cluster_values"][0]["condition"],"NAFL")
        self.assertEqual(new["donor_cluster_values"][0]["genes"],{"X":2})
        with self.assertRaises(ValueError):relabel(new,spec)

if __name__=="__main__":unittest.main()
