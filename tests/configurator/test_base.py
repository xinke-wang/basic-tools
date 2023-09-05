import unittest

from pjtools.configurator import BaseConfigurator


class TestBaseConfigurator(unittest.TestCase):

    def test_init_and_access(self):
        config = BaseConfigurator({'attr1': 1, 'attr2': 'string'})
        self.assertEqual(config.attr1, 1)
        self.assertEqual(config['attr2'], 'string')

    def test_nested_config(self):
        config = BaseConfigurator({'attr1': {'nested_attr': 2}})
        self.assertIsInstance(config.attr1, BaseConfigurator)
        self.assertEqual(config.attr1.nested_attr, 2)

    def test_merge(self):
        config1 = BaseConfigurator({'attr1': 1, 'nested': {'nested_attr1': 1}})

        config2 = BaseConfigurator({'attr2': 2, 'nested': {'nested_attr2': 2}})

        config1.merge(config2)

        self.assertEqual(config1.attr1, 1)
        self.assertEqual(config1.attr2, 2)
        self.assertEqual(config1.nested.nested_attr1, 1)
        self.assertEqual(config1.nested.nested_attr2, 2)

    def test_set_item(self):
        config = BaseConfigurator()
        config['attr1'] = 1
        self.assertEqual(config.attr1, 1)

    def test_set_attr(self):
        config = BaseConfigurator()
        config.attr1 = 1
        self.assertEqual(config['attr1'], 1)
