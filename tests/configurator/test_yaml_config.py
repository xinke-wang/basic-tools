import os
import tempfile
import unittest

from pjtools.configurator.configurator import YAMLConfigurator


class TestYAMLConfigurator(unittest.TestCase):

    def setUp(self):
        self.config = YAMLConfigurator.fromfile('tests/data/dummy_config.yaml')

    def test_basic_types(self):
        self.assertEqual(self.config.learning_rate, 0.001)
        self.assertEqual(self.config.momentum, 0.9)
        self.assertEqual(self.config.optimizer, 'Adam')
        self.assertEqual(self.config.use_cuda, True)

    def test_collections(self):
        self.assertEqual(self.config.layers, [64, 128, 256])
        self.assertEqual(self.config.input_shape, [1, 28, 28])

    def test_dict(self):
        self.assertEqual(self.config.training_params['batch_size'], 64)
        self.assertEqual(self.config.training_params['epochs'], 20)
        self.assertEqual(self.config.training_params['verbose'], 1)

    def test_nested_dict(self):
        self.assertEqual(self.config.data_transforms['train']['normalize'],
                         True)
        self.assertEqual(self.config.data_transforms['train']['resize'],
                         [256, 256])
        self.assertEqual(self.config.data_transforms['val']['normalize'], True)
        self.assertEqual(self.config.data_transforms['val']['resize'],
                         [128, 128])
        self.assertEqual(self.config.data_transforms['val']['flip'], True)

    def test_additional_field(self):
        self.assertEqual(self.config.additional_info,
                         'This is a sample config')

    def test_dump_and_load(self):
        with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w+t') as tmp:
            tmp_path = tmp.name
            self.config.dumpfile(tmp_path, format='yaml')
            loaded_config = YAMLConfigurator.fromfile(tmp_path)
            self.assertEqual(loaded_config.to_dict(), self.config.to_dict())

    def test_env_var_loading(self):
        os.environ['PJTOOLS_DUMMY_TEST_DATABASE_URL'] = '127.0.0.1'
        config = YAMLConfigurator.fromfile('tests/data/dummy_config.json')
        self.assertEqual(config.database.url, '127.0.0.1')
        del os.environ['PJTOOLS_DUMMY_TEST_DATABASE_URL']
