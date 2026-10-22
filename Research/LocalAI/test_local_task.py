import unittest
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


if __name__ == '__main__':
    unittest.main()
