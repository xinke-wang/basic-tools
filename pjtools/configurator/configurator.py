import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from pjtools.registries import CONFIGURATOR_REGISTRY

from .base import BaseConfigurator


@CONFIGURATOR_REGISTRY.register('json')
class JSONConfigurator(BaseConfigurator):
    """Configuration class for reading JSON-based configuration files.

    Example:
        config = JSONConfigurator.fromfile("config.json")
        print(config.some_attribute)
    """

    @classmethod
    def fromfile(cls, filename: str) -> 'JSONConfigurator':
        """Create a JSONConfigurator instance from a JSON file.

        Args:
            filename (str): The name of the JSON file to read.

        Returns:
            JSONConfigurator: An instance of JSONConfigurator initialized with
                data from the JSON file.
        """
        config_dict = cls._load_json_config(filename)
        return cls(config_dict)

    @staticmethod
    def _load_json_config(filename: str) -> Dict[str, Any]:
        """Load a configuration from a JSON file.

        Args:
            filename (str): The name of the JSON file to read.

        Returns:
            Dict[str, Any]: A dictionary containing the configuration data.
        """
        filepath = Path(filename).resolve()
        if not filepath.exists():
            raise FileNotFoundError(f'File {filename} does not exist')

        with open(filepath, 'r') as f:
            config_dict = json.load(f)

        return config_dict


@CONFIGURATOR_REGISTRY.register('py')
class PyConfigurator(BaseConfigurator):
    """Configuration class for reading Python-based configuration files.

    This class provides methods for loading and merging configurations
    from Python files.

    Attributes:
        _base_ (Optional[List[str]]): A list of base configuration files to
            merge from.

    Example:
        config = PyConfigurator.fromfile("config.py")
        print(config.some_attribute)
    """

    def __init__(self,
                 config_dict: Optional[Dict[str, Any]] = None,
                 base_files: Optional[List[str]] = None) -> None:
        """Initialize the PyConfigurator object.

        Args:
            config_dict (Optional[Dict[str, Any]]): Dictionary containing
                configuration attributes.
            base_files (Optional[List[str]]): List of filenames of the base
                configuration files.
        """
        super().__init__(config_dict)
        if base_files:
            self._base_ = base_files

    @classmethod
    def fromfile(cls, filename: str) -> 'PyConfigurator':
        """Load a configuration from a Python file.

        Args:
            filename (str): The filename of the Python configuration file.

        Returns:
            PyConfigurator: A PyConfigurator object with the loaded
                configuration.
        """
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
        """Load a Python configuration file.

        Args:
            filename (str): The filename of the Python configuration file.

        Returns:
            Dict[str, Any]: A dictionary containing the attributes from the
                loaded Python file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        filepath = Path(filename).resolve()
        if not filepath.exists():
            raise FileNotFoundError(f'File {filename} does not exist')

        module_name = filepath.stem
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        config_module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(config_module)

        base_files = getattr(config_module, '_base_', None)

        config_dict = {}

        for attribute_name in dir(config_module):
            if not attribute_name.startswith('_'):
                attribute = getattr(config_module, attribute_name)
                config_dict[attribute_name] = attribute

        return config_dict, base_files


@CONFIGURATOR_REGISTRY.register('yaml')
class YAMLConfigurator(BaseConfigurator):
    """Configuration class for reading YAML-based configuration files.

    Example:
        config = YAMLConfigurator.fromfile("config.yaml")
        print(config.some_attribute)
    """

    @classmethod
    def fromfile(cls, filename: str) -> 'YAMLConfigurator':
        """Create a YAMLConfigurator instance from a YAML file.

        Args:
            filename (str): The name of the YAML file to read.

        Returns:
            YAMLConfigurator: An instance of YAMLConfigurator initialized with
                data from the YAML file.
        """
        config_dict = cls._load_yaml_config(filename)
        return cls(config_dict)

    @staticmethod
    def _load_yaml_config(filename: str) -> Dict[str, Any]:
        """Load a configuration from a YAML file.

        Args:
            filename (str): The name of the YAML file to read.

        Returns:
            Dict[str, Any]: A dictionary containing the configuration data.
        """
        filepath = Path(filename).resolve()
        if not filepath.exists():
            raise FileNotFoundError(f'File {filename} does not exist')

        with open(filepath, 'r') as f:
            config_dict = yaml.safe_load(f)

        return config_dict


class AutoConfigurator(BaseConfigurator):
    """Automatically select the appropriate configurator."""

    CONFIGURATOR_REGISTRY = {
        'json': JSONConfigurator,
        'py': PyConfigurator,
        'yaml': YAMLConfigurator
    }

    @classmethod
    def fromfile(cls, filename: str) -> 'BaseConfigurator':
        """Determine which configurator to use based on the file extension and
        load the file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            BaseConfigurator: An instance of the appropriate configurator class
                initialized with data from the file.
        """
        # Determine the file extension
        file_extension = Path(filename).suffix[1:]

        # Look up the correct configurator class in the registry
        configurator_class = CONFIGURATOR_REGISTRY.get(file_extension)

        if configurator_class is None:
            raise ValueError(f"Unsupported file extension '{file_extension}'")

        # Load the configuration using the selected configurator class
        return configurator_class.fromfile(filename)
