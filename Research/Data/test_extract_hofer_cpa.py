import unittest
import contextlib
import hashlib
import io
from pathlib import Path
import tempfile
from unittest.mock import patch
import extract_hofer_cpa as importer
from extract_hofer_cpa import extract

# Synthetic parser fixture only; not experimental measurements.
FIXTURE = '''
CCl Healthy controls Diseased animals 1 week regression 2 weeks regression
(C-) n=2 (C+) n=3 (R1) n=4 (R2) n=5
Fibrosis (CPA %) 1.0 (0.8-1.2) 10.0 (9.0-11.0) 8.0 (7.0-9.0) 4.0 (3.0-5.0)
TAA Healthy controls Diseased animals 1 week regression 2 weeks regression
(C-) n=9 (C+) n=9 (R1) n=9 (R2) n=9
Fibrosis (CPA %) 2.0 (1.0-3.0) 20.0 (19.0-21.0) 18.0 (17.0-19.0) 14.0 (13.0-15.0)
'''


class ExtractionTests(unittest.TestCase):
    def test_ccl4_is_not_pooled_with_taa_and_controls_have_no_fake_time(self):
        rows = extract(FIXTURE)
        self.assertEqual([r['n_animals'] for r in rows], [2, 3, 4, 5])
        self.assertEqual([r['median_cpa_percent'] for r in rows], [1, 10, 8, 4])
        self.assertEqual([r['days_after_withdrawal'] for r in rows], [None, 0, 7, 14])

    def test_missing_ccl4_marker_is_not_replaced_with_taa(self):
        with self.assertRaises(ValueError): extract(FIXTURE.replace('CCl Healthy', 'Unknown Healthy'))

    def test_missing_count_fails(self):
        with self.assertRaises(ValueError): extract(FIXTURE.replace('(R1) n=4', ''))

    def test_reversed_quartiles_fail(self):
        with self.assertRaises(ValueError): extract(FIXTURE.replace('10.0 (9.0-11.0)', '10.0 (12.0-11.0)'))

    def test_duplicate_cpa_row_fails(self):
        line = 'Fibrosis (CPA %) 1.0 (0.8-1.2) 10.0 (9.0-11.0) 8.0 (7.0-9.0) 4.0 (3.0-5.0)'
        with self.assertRaises(ValueError): extract(FIXTURE.replace(line, line + '\n' + line))

    def test_cli_checks_transcription_and_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf, md, out = root/'source.pdf', root/'source.md', root/'data.csv'
            pdf.write_bytes(b'synthetic fixture, not a publication')
            md.write_text(FIXTURE)
            argv = ['importer', '--markdown', str(md), '--source-pdf', str(pdf), '--output', str(out)]
            with patch('sys.argv', argv), \
                 patch.object(importer, 'PDF_SHA256', hashlib.sha256(pdf.read_bytes()).hexdigest()), \
                 patch.object(importer, 'MARKDOWN_SHA256', hashlib.sha256(md.read_bytes()).hexdigest()):
                md.write_text(FIXTURE + '\nchanged')
                with self.assertRaises(ValueError): importer.main()
                self.assertFalse(out.exists())
                md.write_text(FIXTURE)
                provenance = out.with_suffix('.provenance.json')
                provenance.write_text('prior evidence')
                with self.assertRaises(FileExistsError): importer.main()
                self.assertFalse(out.exists())
                self.assertEqual(provenance.read_text(), 'prior evidence')
                provenance.unlink()
                with contextlib.redirect_stdout(io.StringIO()): importer.main()
                before = out.read_bytes(), provenance.read_bytes()
                with self.assertRaises(FileExistsError): importer.main()
                self.assertEqual((out.read_bytes(), provenance.read_bytes()), before)


if __name__ == '__main__':
    unittest.main()
