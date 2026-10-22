import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import run_local_task as worker
from run_local_task import validate_model


class ModelBoundaryTests(unittest.TestCase):
    def test_installed_digest_required(self):
        with self.assertRaises(ValueError):
            validate_model({'models': [{'name': 'x', 'digest': 'old'}]}, 'x', 'new', {'details': {'format': 'gguf'}})

    def test_cloud_model_rejected_even_through_local_endpoint(self):
        for remote in ('remote_host', 'remote_model'):
            with self.assertRaises(ValueError):
                validate_model({'models': [{'name': 'x', 'digest': 'd', remote: 'cloud'}]}, 'x', 'd', {'details': {'format': 'gguf'}})

    def test_local_gguf_allowed_but_does_not_prove_inference(self):
        result = validate_model({'models': [{'name': 'x', 'digest': 'd'}]}, 'x', 'd', {'details': {'format': 'gguf'}})
        self.assertEqual(result['digest'], 'd')

    def test_loaded_runner_never_proves_inference_even_after_goose_exit(self):
        # Synthetic process/API fixtures: this test performs no actual inference.
        for returncode in (0, 7):
            with self.subTest(returncode=returncode), tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)
                task = folder / 'input.txt'
                task.write_text('Translate this synthetic fixture.')
                output = folder / 'output'
                process = Mock(returncode=returncode)
                process.poll.side_effect = [None, returncode]
                ps = iter([{'models': []}, {'models': [{'digest': 'd'}]}, {'models': []}])

                def api(route, payload=None):
                    if route == 'ps':
                        return next(ps)
                    return {'show': {'details': {'format': 'gguf'}},
                            'tags': {'models': [{'name': 'x', 'digest': 'd'}]},
                            'version': {'version': 'fixture'}, 'generate': {}}[route]

                argv = ['worker', '--model', 'x', '--digest', 'd', '--task', str(task), '--output', str(output)]
                with patch('sys.argv', argv), patch.object(worker, 'api', side_effect=api), \
                     patch.object(worker.shutil, 'which', return_value='/fixture/goose'), \
                     patch.object(worker.subprocess, 'check_output', return_value='goose fixture'), \
                     patch.object(worker.subprocess, 'Popen', return_value=process), \
                     patch.object(worker, 'local_runners', return_value=[{'model_blob_exists': True, 'model_blob_bytes': 1}]), \
                     patch.object(worker.time, 'monotonic', return_value=0), patch.object(worker.time, 'sleep'):
                    worker.main()
                report = json.loads((output / 'audit.json').read_text())
                self.assertFalse(report['inference_verified'])
                self.assertEqual(report['status'], 'completed_pending_review' if returncode == 0 else 'failed')


if __name__ == '__main__':
    unittest.main()
