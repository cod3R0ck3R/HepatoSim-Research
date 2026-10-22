import json
from pathlib import Path
import tempfile
import unittest
import export_public as exporter


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'workspace/outputs/project'
        self.source.mkdir(parents=True)
        self.output = self.root / 'public'

    def test_numeric_data_and_source_preserved_metadata_redaction_recorded(self):
        args = ['/fixture/KaSim', '/fixture/vendor/HSC_model_Kappa/model.ka', '-l', '243', '-p', '0.5', '-seed', '101', '-mode', 'batch', '-d', '/fixture/seed-101']
        data = {'argv': args, 'seed': 101, 'trace_sha256': exporter.digest(b'time,value\n0,0.5\n')}
        original = exporter.json_bytes(data)
        (self.source / 'run.json').write_bytes(original)
        (self.source / 'trace.csv').write_bytes(b'time,value\n0,0.5\n')
        exporter.export(self.source, self.output)
        self.assertEqual((self.source / 'run.json').read_bytes(), original)
        self.assertEqual((self.source / 'trace.csv').read_bytes(), (self.output / 'trace.csv').read_bytes())
        receipt = json.loads((self.output / 'manifest-redaction.json').read_text())
        self.assertEqual(receipt['original_sha256'], exporter.digest(original))
        self.assertEqual(receipt['changed_fields'], ['argv[0]', 'argv[1]', 'argv[11]'])
        self.assertEqual(json.loads((self.output / 'run.json').read_text())['seed'], 101)

    def test_trace_comments_redacted_but_numeric_bytes_unchanged(self):
        data = ('# source ' + str(self.source / 'model.ka') + '\n').encode() + b'time,value\n0,0.5000\n'
        result = exporter.redact_trace(data, self.source)
        self.assertNotIn(str(self.source).encode(), result)
        self.assertEqual(exporter.numeric_payload(result), exporter.numeric_payload(data))

    def test_private_path_outside_json_rejected_before_destination_exists(self):
        (self.source / 'README.md').write_text(str(Path.home() / 'private/secret'))
        with self.assertRaisesRegex(ValueError, 'private content'):
            exporter.export(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_output_never_overwritten(self):
        self.output.mkdir()
        with self.assertRaisesRegex(ValueError, 'must be new'):
            exporter.export(self.source, self.output)


if __name__ == '__main__':
    unittest.main()
