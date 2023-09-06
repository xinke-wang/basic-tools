import json

import yaml

from pjtools.registries import DUMPER_REGISTRY


@DUMPER_REGISTRY.register('json')
def json_dumper(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@DUMPER_REGISTRY.register('yaml')
def yaml_dumper(data, filename):
    with open(filename, 'w') as f:
        yaml.dump(data, f)


@DUMPER_REGISTRY.register('py')
def py_dumper(data, filename):
    with open(filename, 'w') as f:
        for key, value in data.items():
            f.write(f'{key} = {repr(value)}\n')
