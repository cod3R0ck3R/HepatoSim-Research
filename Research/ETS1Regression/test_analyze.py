import copy
import tempfile
import unittest
from pathlib import Path
import zipfile
import analyze


class AuditTests(unittest.TestCase):
    def test_exact_normalization_and_permutation_of_rows(self):
        b = [[2, 4], [4, 8], [1, 2], [2, 4]]
        c = [[4/3, 2/3], [2/3, 4/3], [2/3, 1/3], [1/3, 2/3]]
        r = analyze.compare(b, c, [5e-6, .002])
        self.assertTrue(all(r['normalization_pass_by_tolerance'].values()))
        self.assertEqual(r['descriptive_ratios']['derived_from_B']['knockout_vs_control_ratio_of_remaining_fractions'], 1)

    def test_mismatch_and_unequal_n_fail(self):
        b = [[2, 4]]*4
        c = [[2/3, 4/3]]*3 + [[1, 1]]
        self.assertFalse(analyze.compare(b, c, [5e-6])['normalization_pass_by_tolerance']['5e-06'])
        c[3] = [2/3, 1, 4/3]
        self.assertFalse(analyze.compare(b, c, [.002])['counts_equal'])

    def test_invalid_values_and_layout_rejected(self):
        for invalid in [0, float('nan'), -1]:
            with self.assertRaises(ValueError): analyze.compare([[1, invalid]]*4, [[1, 2]]*4, [.002])
        with self.assertRaises(ValueError): analyze.extract({'A1': 'Wrong unit'})

    def test_excel_inline_string_and_literal(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'test.xlsx'
            with zipfile.ZipFile(p, 'w') as z:
                z.writestr('xl/workbook.xml', '<workbook xmlns="'+analyze.NS['m']+'" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Fig. 2B" r:id="r1"/></sheets></workbook>')
                z.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="r1" Target="worksheets/sheet1.xml"/></Relationships>')
                z.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="'+analyze.NS['m']+'"><sheetData><row><c r="A1" t="inlineStr"><is><t>ETS1ΔHSC</t></is></c><c r="A4"><v>2.3</v></c></row></sheetData></worksheet>')
            self.assertEqual(analyze.worksheet(p,'Fig. 2B'), {'A1':'ETS1ΔHSC','A4':2.3})
            with self.assertRaises(ValueError): analyze.worksheet(p,'Absent')

    def test_markdown_group_extraction(self):
        t='## Fig. 2B\n| Sirius Red+ area (%) | x | x | x |\n| --- | --- | --- | --- |\n| CCl4 | NaN | Regression | NaN |\n| ETS1flox/flox | ETS1ΔHSC | ETS1flox/flox | ETS1ΔHSC |\n| 1 | 2 | 3 | 4 |\n| 5 | 6 | 7 | 8 |\n'
        self.assertEqual(analyze.from_markdown(t,'Fig. 2B'),[[1,5],[2,6],[3,7],[4,8]])

    def test_conversion_rounding_not_source_repair(self):
        self.assertLess(analyze.check_conversion([[1/3, 2/3]], [[.333333, .666667]]), 5e-6)
        with self.assertRaises(ValueError): analyze.check_conversion([[1, 2]], [[2, 1]])
        with self.assertRaises(ValueError): analyze.check_conversion([[1, 2]], [[1]])

if __name__ == '__main__': unittest.main()
