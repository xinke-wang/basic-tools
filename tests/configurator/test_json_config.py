import os
import tempfile
import unittest

from pjtools.configurator.configurator import JSONConfigurator


class TestJSONConfigurator(unittest.TestCase):

    def setUp(self):
        self.default_config = JSONConfigurator.fromfile(
            'tests/data/dummy_config.json')

    def test_load_from_file(self):
        config = self.default_config

        # Test database configuration
        self.assertEqual(config.database.host, 'localhost')
        self.assertEqual(config.database.port, 5432)
        self.assertEqual(config.database.user, 'root')
        self.assertEqual(config.database.password, 'password')

        # Test API configuration
        self.assertEqual(config.api.version, 'v1')
        self.assertEqual(config.api.endpoint, '/api/')

        # Test logging configuration
        self.assertEqual(config.logging.level, 'INFO')

    def test_to_dict(self):
        config_dict = self.default_config.to_dict()

        self.assertEqual(config_dict['database']['host'], 'localhost')
        self.assertEqual(config_dict['database']['port'], 5432)
        self.assertEqual(config_dict['database']['user'], 'root')
        self.assertEqual(config_dict['database']['password'], 'password')
        self.assertEqual(config_dict['api']['version'], 'v1')
        self.assertEqual(config_dict['api']['endpoint'], '/api/')
        self.assertEqual(config_dict['logging']['level'], 'INFO')

    def test_dump_and_load(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
            self.default_config.dumpfile(tmp_path, format='json')

            loaded_config = JSONConfigurator.fromfile(tmp_path)

            self.assertEqual(loaded_config.to_dict(),
                             self.default_config.to_dict())

    def test_env_var_loading(self):
        os.environ['PJTOOLS_DUMMY_TEST_DATABASE_URL'] = '127.0.0.1'
        config = JSONConfigurator.fromfile('tests/data/dummy_config.json')
        self.assertEqual(config.database.url, '127.0.0.1')
        del os.environ['PJTOOLS_DUMMY_TEST_DATABASE_URL']
