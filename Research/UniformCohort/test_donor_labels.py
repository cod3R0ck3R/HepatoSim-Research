import unittest
from audit_donor_labels import geo_labels


class DescriptionTests(unittest.TestCase):
    def xml(self,description):
        return ('<MINiML xmlns="http://www.ncbi.nlm.nih.gov/geo/info/MINiML"><Sample iid="GSM7830569"><Title>JB_321, snRNAseq</Title><Channel><Characteristics tag="tissue">liver</Characteristics></Channel>'+description+'</Sample></MINiML>').encode()

    def test_description_read_even_when_characteristics_only_contains_tissue(self):
        result=geo_labels(self.xml('<Description> MASL </Description>'))
        self.assertEqual(result['JB321']['geo_group'],'NAFL')
        self.assertEqual(result['JB321']['accession'],'GSM7830569')

    def test_missing_or_unknown_description_is_not_inferred(self):
        for field in ['', '<Description>unknown</Description>']:
            with self.subTest(field=field),self.assertRaises(ValueError):geo_labels(self.xml(field))


if __name__=='__main__':unittest.main()
