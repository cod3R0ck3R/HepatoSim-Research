"""Archive/provenance and budget boundaries; no new biological simulation."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import run_mechanism_pilot as pilot


class MechanismPilotTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name) / 'results'
        self.output.mkdir()
        self.spec = pilot.resume.load_spec(pilot.HERE / 'benchmark-v1.3.0.json')

    def test_archive_reuse_skips_five_real_runs_without_charging_new_budget(self):
        pilot.reuse_runs(self.output, self.spec)
        _, states = pilot.resume.inspect(self.output, self.spec)
        self.assertEqual(sum(s['analysis_status'] == 'eligible' for s in states), 5)
        self.assertEqual(pilot.consumed_seconds(self.output, self.spec), 0)
        job, remaining = pilot.next_job(self.output, self.spec)
        self.assertEqual(job['job_id'], 'without_reinactivation-101')
        self.assertEqual(remaining, 5400)

    def test_reused_manifest_is_verified_again_after_copy(self):
        pilot.reuse_runs(self.output, self.spec)
        manifest = self.output / 'repository_default-102/run.json'
        before = manifest.read_text()
        manifest.write_text(before + '\n')
        with self.assertRaisesRegex(ValueError, 'manifest changed'):
            pilot.reuse_runs(self.output, self.spec)
        self.assertEqual(manifest.read_text(), before + '\n')

    def test_missing_archive_control_is_never_silently_resimulated(self):
        with self.assertRaisesRegex(ValueError, 'Archived control missing'):
            pilot.next_job(self.output, self.spec)

    def test_orphan_run_blocks_retry_without_deleting_evidence(self):
        pilot.reuse_runs(self.output, self.spec)
        folder = self.output / 'without_reinactivation-101'
        folder.mkdir()
        marker = folder / 'partial.txt'
        marker.write_text('interrupted evidence')
        with self.assertRaisesRegex(ValueError, 'no automatic retry'):
            pilot.next_job(self.output, self.spec)
        self.assertEqual(marker.read_text(), 'interrupted evidence')

    def test_budget_requires_full_timeout_window_before_next_start(self):
        pilot.reuse_runs(self.output, self.spec)
        spec = copy.deepcopy(self.spec)
        spec['budget']['total_simulation_wall_seconds'] = 899
        with patch.object(pilot.resume, 'inspect', return_value=pilot.resume.inspect(self.output, self.spec)):
            with self.assertRaisesRegex(ValueError, 'complete timeout window'):
                pilot.next_job(self.output, spec)

    def test_unknown_negative_nonfinite_and_boolean_costs_are_not_reset(self):
        folder = self.output / 'without_reinactivation-101'
        folder.mkdir()
        for value in (None, -1, float('nan'), float('inf'), True):
            with self.subTest(value=value):
                (folder / 'run.json').write_text(json.dumps({'wall_seconds': value}))
                with self.assertRaisesRegex(ValueError, 'Unknown or invalid'):
                    pilot.consumed_seconds(self.output, self.spec)

    def test_completed_and_timeout_costs_are_charged(self):
        for name, cost in (('without_reinactivation-101', 150), ('without_reinactivation-102', 900)):
            folder = self.output / name
            folder.mkdir()
            (folder / 'run.json').write_text(json.dumps({'wall_seconds': cost}))
        self.assertEqual(pilot.consumed_seconds(self.output, self.spec), 1050)

    def test_read_only_command_creates_nothing_and_never_runs_kasim(self):
        absent = self.output / 'absent'
        with patch.object(pilot.runner, 'run_job', side_effect=AssertionError('must not execute')):
            self.assertEqual(pilot.main(['--output', str(absent)]), 0)
        self.assertFalse(absent.exists())

    def test_one_invocation_launches_only_one_run_and_preserves_remaining_work(self):
        executable = self.output.parent / 'mock-runtime'
        runtime_hash = json.loads((pilot.HERE / 'runtime-lock.json').read_text())['executable_sha256']
        digest = pilot.runner.digest
        def test_digest(path):
            return runtime_hash if Path(path) == executable else digest(path)
        def simulated_worker(job, spec, runtime, output, deadline):
            # Test-only identity fixture; copied values are not mechanism predictions.
            archived = pilot.HERE / 'results/benchmark-v1.1/repository_default-101'
            folder = output / job['job_id']
            folder.mkdir()
            shutil.copyfile(archived / 'trace.csv', folder / 'trace.csv')
            record = json.loads((archived / 'run.json').read_text())
            record.update(job_id=job['job_id'], condition=job['id'], wall_seconds=0.01,
                          model_sha256=digest(pilot.HERE / 'vendor/HSC_model_Kappa' / job['file']))
            record['argv'][1] = str(pilot.HERE / 'vendor/HSC_model_Kappa' / job['file'])
            record['argv'][11] = str(folder)
            (folder / 'run.json').write_text(json.dumps(record))
            return record
        with patch.object(pilot.runner, 'digest', side_effect=test_digest), \
                patch.object(pilot.runner, 'run_job', side_effect=simulated_worker) as worker, \
                patch.object(pilot, 'PROJECT', self.output.parent):
            self.assertEqual(pilot.execute_one(self.output, self.spec, pilot.HERE / 'benchmark-v1.3.0.json', executable), 0)
        self.assertEqual(worker.call_count, 1)
        state = json.loads((self.output / 'resume-state.json').read_text())
        self.assertEqual(len(state['remaining_jobs']), 5)
        self.assertEqual(state['blocked_jobs'], [])
        self.assertEqual(state['new_simulation_seconds'], 0.01)


if __name__ == '__main__':
    unittest.main()
