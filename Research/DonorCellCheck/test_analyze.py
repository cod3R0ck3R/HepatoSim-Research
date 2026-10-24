import io
import unittest
import numpy as np
from analyze import join_barcodes, aggregate, contrast, coordinates
from reference_sensitivity import common_totals, normalize_ids


class DonorTests(unittest.TestCase):
    def test_version_removal_preserves_identity_and_rejects_ambiguity(self):
        self.assertEqual(normalize_ids([['ENSG001.12','A'],['ENSG002','B']]),[['ENSG001','A'],['ENSG002','B']])
        with self.assertRaises(ValueError): normalize_ids([['ENSG001.1','A'],['ENSG001.2','B']])

    def test_common_reference_denominator(self):
        raw=b'%%MatrixMarket matrix coordinate integer general\n2 3 5\n1 1 2\n2 1 3\n1 2 999\n1 3 7\n2 3 11\n'
        value=common_totals(io.BytesIO(raw),np.array([0,2]),np.array([True,False]),3)
        self.assertEqual(value.tolist(),[2,7])

    def test_join_order_and_missing(self):
        pos,types,n=join_barcodes(io.StringIO('a\nb\nc\n'),{'c':'HSC','a':'Mac'})
        self.assertEqual(pos.tolist(),[0,2]);self.assertEqual(types.tolist(),['Mac','HSC']);self.assertEqual(n,3)
        with self.assertRaises(ValueError): join_barcodes(io.StringIO('a\n'),{'c':'HSC'})
        with self.assertRaises(ValueError): join_barcodes(io.StringIO('a\na\n'),{'a':'Mac'})

    def test_excludes_unannotated_and_sums_exactly(self):
        raw=b'%%MatrixMarket matrix coordinate integer general\n2 3 5\n1 1 2\n2 1 3\n1 2 999\n1 3 7\n2 3 11\n'
        total,target,dims=aggregate(io.BytesIO(raw),np.array([0,2]),2,3,[0,1])
        self.assertEqual(total.tolist(),[5,18]);self.assertEqual(target.tolist(),[[2,7],[3,11]])
        self.assertEqual(dims,(2,3,5))

    def test_raw_droplet_capacity_is_opt_in(self):
        raw=b'%%MatrixMarket matrix coordinate integer general\n1 100001 1\n1 100001 2\n'
        with self.assertRaises(ValueError): list(coordinates(io.BytesIO(raw)))
        self.assertEqual(list(coordinates(io.BytesIO(raw),max_cells=100001))[0][3].tolist(),[2])

    def test_duplicate_and_truncated_coordinates_rejected(self):
        for rows in [b'1 1 2\n1 1 3\n',b'1 1 2\n']:
            with self.assertRaises(ValueError): list(coordinates(io.BytesIO(b'%%MatrixMarket matrix coordinate integer general\n1 1 2\n'+rows)))

    def test_permutation_resolution_and_donor_loo(self):
        r=contrast([4,5,6],[1,2,3]);self.assertEqual(r['exact_permutation_p'],.1)
        self.assertTrue(r['loo_direction_stable']);self.assertEqual(contrast([1,1,1],[1,1,1])['exact_permutation_p'],1)


if __name__=='__main__': unittest.main()
