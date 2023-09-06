import json
from typing import Any, Dict

import yaml

from pjtools.registries import DUMPER_REGISTRY


@DUMPER_REGISTRY.register('json')
def json_dumper(data: Dict[str, Any], filename: str) -> None:
    """Dump data to a JSON file.

    Args:
        data (Dict[str, Any]): The data to be dumped.
        filename (str): The name of the file where data will be dumped.

    Example:
        json_dumper({'key': 'value'}, 'config.json')
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@DUMPER_REGISTRY.register('yaml')
def yaml_dumper(data: Dict[str, Any], filename: str) -> None:
    """Dump data to a YAML file.

    Args:
        data (Dict[str, Any]): The data to be dumped.
        filename (str): The name of the file where data will be dumped.

    Example:
        yaml_dumper({'key': 'value'}, 'config.yaml')
    """
    with open(filename, 'w') as f:
        yaml.dump(data, f)


@DUMPER_REGISTRY.register('py')
def py_dumper(data: Dict[str, Any], filename: str) -> None:
    """Dump data to a Python file.

    Args:
        data (Dict[str, Any]): The data to be dumped.
        filename (str): The name of the file where data will be dumped.

    Example:
        py_dumper({'key': 'value'}, 'config.py')
    """
    with open(filename, 'w') as f:
        for key, value in data.items():
            f.write(f'{key} = {repr(value)}\n')
