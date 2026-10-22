"""Resume checks use archived real output; no simulation or model-generated values."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import resume_reference as resume


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'results'
        self.output.mkdir()
        self.spec = resume.load_spec(resume.HERE / 'benchmark-v1.2.0.json')

    def test_real_baseline_is_reused_without_modification(self):
        resume.reuse_baseline(self.output, self.spec)
        _, states = resume.inspect(self.output, self.spec)
        self.assertEqual([s['analysis_status'] for s in states], ['eligible', 'missing', 'missing'])
        self.assertIn(resume.verify_baseline_manifest(self.output / 'repository_default-101', self.spec['reuse']),
                      ('original_bytes_verified', 'published_bytes_verified_original_digest_is_exporter_attestation'))
        self.assertEqual(resume.consumed_seconds(self.output, self.spec), 0)

    def test_corrupted_trace_cannot_be_skipped_as_success(self):
        resume.reuse_baseline(self.output, self.spec)
        trace = self.output / 'repository_default-101/trace.csv'
        trace.write_bytes(trace.read_bytes() + b'\ncorruption\n')
        _, states = resume.inspect(self.output, self.spec)
        self.assertEqual(states[0]['analysis_status'], 'invalid_input')

    def test_changed_source_manifest_is_rejected_before_copy(self):
        spec = copy.deepcopy(self.spec)
        spec['reuse']['run_manifest_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'manifest changed'):
            resume.reuse_baseline(self.output, spec)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_orphan_folder_is_not_treated_as_missing(self):
        (self.output / 'seed-replay-101').mkdir()
        _, states = resume.inspect(self.output, self.spec)
        self.assertEqual(states[1]['analysis_status'], 'invalid_input')

    def test_interrupted_cost_is_not_reset(self):
        folder = self.output / 'seed-replay-101'
        folder.mkdir()
        (folder / 'run.json').write_text('{"status":"not_started"}')
        with self.assertRaisesRegex(ValueError, 'unknown cost'):
            resume.consumed_seconds(self.output, self.spec)

    def test_completed_and_timeout_costs_accumulate(self):
        for name, cost in [('seed-replay-101', 50), ('grid-quarter-day-101', 900)]:
            folder = self.output / name
            folder.mkdir()
            (folder / 'run.json').write_text(json.dumps({'wall_seconds': cost}))
        self.assertEqual(resume.consumed_seconds(self.output, self.spec), 950)

    def test_atomic_json_preserves_previous_file_on_serialization_error(self):
        path = self.output / 'state.json'
        path.write_text('{"verified":true}\n')
        with self.assertRaises(ValueError):
            resume.atomic_json(path, {'bad': float('nan')})
        self.assertEqual(json.loads(path.read_text()), {'verified': True})

    def test_public_manifest_requires_matching_explicit_redaction_receipt(self):
        resume.reuse_baseline(self.output, self.spec)
        folder = self.output / 'repository_default-101'
        path = folder / 'run.json'
        record = json.loads(path.read_text())
        record['argv'][0] = 'KaSim'
        record['argv'][1] = 'vendor/HSC_model_Kappa/reactMFB-with-inactivation.ka'
        record['argv'][11] = 'repository_default-101'
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'manifest changed'):
            resume.verify_baseline_manifest(folder, self.spec['reuse'])
        receipt = {'original_sha256': self.spec['reuse']['run_manifest_sha256'],
                   'published_sha256': resume.runner.digest(path),
                   'changed_fields': ['argv[0]', 'argv[1]', 'argv[11]'],
                   'trace_sha256': self.spec['reuse']['trace_sha256'],
                   'published_trace_sha256': resume.runner.digest(folder / 'trace.csv'),
                   'numeric_payload_sha256': resume.analysis.sha256_bytes(b''.join(line for line in (folder / 'trace.csv').read_bytes().splitlines(keepends=True) if not line.startswith(b'#')))}
        (folder / 'manifest-redaction.json').write_text(json.dumps(receipt))
        self.assertEqual(resume.verify_baseline_manifest(folder, self.spec['reuse']),
                         'published_bytes_verified_original_digest_is_exporter_attestation')
        path.write_text(path.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'manifest changed'):
            resume.verify_baseline_manifest(folder, self.spec['reuse'])

    def test_check_does_not_start_runtime_or_create_output(self):
        absent = self.output / 'absent'
        with patch.object(resume.runner, 'run_job', side_effect=AssertionError('must not execute')):
            self.assertEqual(resume.main(['--output', str(absent)]), 0)
        self.assertFalse(absent.exists())


if __name__ == '__main__':
    unittest.main()
