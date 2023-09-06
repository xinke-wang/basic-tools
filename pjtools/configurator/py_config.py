import importlib.util
from pathlib import Path
from typing import Any, Dict

from pjtools.configurator import BaseConfigurator


class PyConfigurator(BaseConfigurator):
    """Configuration class for reading Python-based configuration files.

    Example:
        config = PyConfigurator.fromfile("config.py")
        print(config.some_attribute)
    """

    def __init__(self, config_dict=None, base_files=None):
        super().__init__(config_dict)
        if base_files:
            self._base_ = base_files

    @classmethod
    def fromfile(cls, filename):
        config_dict, base_files = cls._load_python_config(filename)

        if base_files is None:
            base_files = []

        if not isinstance(base_files, list):
            base_files = [base_files]

        base_config = cls()
        for base_file in base_files:
            if base_file is not None:
                base_config.merge(cls.fromfile(base_file))
            else:
                raise ValueError('Invalid base_file: None')

        current_config = cls(config_dict)
        base_config.merge(current_config)

        return base_config

    @staticmethod
    def _load_python_config(filename: str) -> Dict[str, Any]:
        filepath = Path(filename).resolve()
        if not filepath.exists():
            raise FileNotFoundError(f'File {filename} does not exist')

        module_name = filepath.stem
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        config_module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(config_module)  # type: ignore

        base_files = getattr(config_module, '_base_', None)

        config_dict = {}

        for attribute_name in dir(config_module):
            if not attribute_name.startswith('_'):
                attribute = getattr(config_module, attribute_name)
                config_dict[attribute_name] = attribute

        return config_dict, base_files
