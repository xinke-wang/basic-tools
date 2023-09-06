import unittest

from pjtools.configurator.configurator import (AutoConfigurator,
                                               JSONConfigurator,
                                               PyConfigurator,
                                               YAMLConfigurator)


class TestAutoConfigurator(unittest.TestCase):

    def test_json_config(self):
        json_file = 'tests/data/dummy_config.json'
        auto_config = AutoConfigurator.fromfile(str(json_file))
        json_config = JSONConfigurator.fromfile(str(json_file))
        self.assertEqual(auto_config.to_dict(), json_config.to_dict())

    def test_py_config(self):
        py_file = 'tests/data/dummy_config.py'
        auto_config = AutoConfigurator.fromfile(str(py_file))
        py_config = PyConfigurator.fromfile(str(py_file))
        self.assertEqual(auto_config.to_dict(), py_config.to_dict())

    def test_yaml_config(self):
        yaml_file = 'tests/data/dummy_config.yaml'
        auto_config = AutoConfigurator.fromfile(str(yaml_file))
        yaml_config = YAMLConfigurator.fromfile(str(yaml_file))
        self.assertEqual(auto_config.to_dict(), yaml_config.to_dict())
