import pytest

from pjtools.registry import Registry


def test_registry_basic_functionality():

    reg = Registry('TestRegistry')

    class ExampleModule:
        pass

    reg.register('example', ExampleModule)
    assert 'example' in reg
    assert reg.get('example') is ExampleModule

    with pytest.raises(KeyError):
        reg.get('none_existent_module')

    with pytest.raises(ValueError):
        reg.register('example', ExampleModule)


def test_registry_category():
    reg = Registry('Backbone')
    assert repr(reg).startswith('Backbone: ')
