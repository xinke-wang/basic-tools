from typing import Any, Dict, Type, Union


class BaseConfigurator:
    """Base class for configuration objects.

    Attributes can be accessed either as dict keys or as object attributes.

    Example:
        config = BaseConfigurator({"attr1": 1, "attr2": "string"})
        print(config.attr1)  # Output: 1
        print(config["attr2"])  # Output: "string"
    """

    def __init__(self,
                 config_dict: Union[Dict[str, Any], None] = None) -> None:
        """Initialize a new configuration object.

        Args:
            config_dict: Optional dictionary containing initial configuration
                keys and values.
        """
        if config_dict:
            self._load_from_dict(config_dict)

    def _load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Load attributes from a dictionary.

        Args:
            config_dict: Dictionary containing configuration keys and values.
        """
        for key, value in config_dict.items():
            if isinstance(value, dict):
                self.__dict__[key] = BaseConfigurator(value)
            else:
                self.__dict__[key] = value

    def __getitem__(self, key: str) -> Any:
        """Get an attribute using dict-style key access.

        Args:
            key: Attribute name to retrieve.

        Returns:
            The value of the attribute or None if attribute is not set.
        """
        return self.__dict__.get(key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an attribute using dict-style key-value pairs.

        Args:
            key: Attribute name.
            value: Attribute value.
        """
        self.__dict__[key] = value

    def __getattr__(self, key: str) -> Any:
        """Get an attribute using attribute-style access.

        Args:
            key: Attribute name to retrieve.

        Returns:
            The value of the attribute or None if attribute is not set.
        """
        return self.__dict__.get(key, None)

    def __setattr__(self, key: str, value: Any) -> None:
        """Set an attribute using attribute-style access.

        Args:
            key: Attribute name.
            value: Attribute value.
        """
        self.__dict__[key] = value

    @classmethod
    def fromfile(cls: Type['BaseConfigurator'],
                 filename: str) -> 'BaseConfigurator':
        """Create a configuration object from a file.

        This is a placeholder method that should be implemented in subclasses.

        Args:
            filename: Name of the configuration file.

        Returns:
            A new configuration object.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    def dumpfile(self, filename: str) -> None:
        """Dump the configuration to a file.

        This is a placeholder method that should be implemented in subclasses.

        Args:
            filename: Name of the output file.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    def merge(self, other_config: 'BaseConfigurator') -> None:
        """Merge another configuration object into this one.

        Args:
            other_config: Another configuration object.
        """
        for key, value in other_config.__dict__.items():
            if key not in self.__dict__:
                self.__dict__[key] = value
            else:
                if isinstance(self.__dict__[key],
                              BaseConfigurator) and isinstance(
                                  value, BaseConfigurator):
                    self.__dict__[key].merge(value)
                else:
                    self.__dict__[key] = value
