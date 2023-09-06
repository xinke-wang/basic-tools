import unittest

from pjtools.registry import Registry


class TestRegistry(unittest.TestCase):

    def test_registry_basic_functionality(self):
        reg = Registry('TestRegistry')

        @reg.register('example')
        class ExampleModule:
            pass

        self.assertIn('example', reg)
        self.assertIs(reg.get('example'), ExampleModule)

        with self.assertRaises(KeyError):
            reg.get('none_existent_module')

        with self.assertRaises(ValueError):
            reg.register('example')(ExampleModule)

    def test_registry_category(self):
        reg = Registry('Backbone')
        self.assertTrue(repr(reg).startswith('Backbone: '))
