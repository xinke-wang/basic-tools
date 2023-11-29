import os
import tempfile
import unittest

from pjtools.configurator.configurator import PyConfigurator


class TestPyConfigurator(unittest.TestCase):

    def setUp(self):
        self.default_config = PyConfigurator.fromfile('tests/data/default.py')
        self.dummy_config = PyConfigurator.fromfile(
            'tests/data/dummy_config.py')

    def test_basic_types(self):
        self.assertEqual(self.dummy_config.learning_rate, 0.001)
        self.assertEqual(self.dummy_config.momentum, 0.95)
        self.assertEqual(self.dummy_config.optimizer,
                         self.default_config.optimizer)
        self.assertEqual(self.dummy_config.use_cuda,
                         self.default_config.use_cuda)

    def test_collections(self):
        self.assertEqual(self.dummy_config.layers, self.default_config.layers)
        self.assertEqual(self.dummy_config.input_shape,
                         self.default_config.input_shape)
        self.assertEqual(self.dummy_config.nested_list,
                         self.default_config.nested_list)
        self.assertEqual(self.dummy_config.nested_tuple,
                         self.default_config.nested_tuple)

    def test_dict(self):
        self.assertEqual(self.dummy_config.training_params['batch_size'], 64)
        self.assertEqual(self.dummy_config.training_params['epochs'], 20)
        self.assertEqual(self.dummy_config.training_params['verbose'], 1)

    def test_nested_dict(self):
        self.assertEqual(
            self.dummy_config.data_transforms['train']['normalize'], True)
        self.assertEqual(self.dummy_config.data_transforms['train']['resize'],
                         (256, 256))
        self.assertEqual(self.dummy_config.data_transforms['val']['normalize'],
                         True)
        self.assertEqual(self.dummy_config.data_transforms['val']['resize'],
                         (128, 128))
        self.assertEqual(self.dummy_config.data_transforms['val']['flip'],
                         True)

    def test_additional_field(self):
        self.assertEqual(self.dummy_config.additional_info,
                         'This is a dummy config')

    def test_dump_and_load(self):
        with tempfile.NamedTemporaryFile(suffix='.py') as tmp:
            tmp_path = tmp.name
            self.default_config.dumpfile(tmp_path)

            loaded_config = PyConfigurator.fromfile(tmp_path)

            self.assertEqual(loaded_config.to_dict(),
                             self.default_config.to_dict())

    def test_env_var_loading(self):
        os.environ[
            'PJTOOLS_DUMMY_TEST_DATABASE_URL'] = 'mysql://user:pass@localhost/dbname'
        config = PyConfigurator.fromfile('tests/data/dummy_config.py')
        self.assertEqual(config.database_url,
                         'mysql://user:pass@localhost/dbname')
        del os.environ['PJTOOLS_DUMMY_TEST_DATABASE_URL']
