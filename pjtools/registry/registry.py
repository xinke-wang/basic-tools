from typing import Any, Type, Union


class Registry:
    """A registry to map strings to classes.

    This registry serves as a centralized place to store and retrieve
    modules or classes, especially useful for the architectures that need
    flexibility in specifying different modules.

    Args:
        category (str): The name of the registry (e.g., 'Backbone', 'Head') to
            distinguish between different module types.
    """

    def __init__(self, category: str) -> None:
        """Initialize the registry with a given category."""
        self._category = category
        self._modules = {}

    def register(self, name: str, module: Type[Any]) -> None:
        """Register a module with a given name.

        Args:
            name (str): The name to register the module under.
            module (Type[Any]): The actual module/class to be registered.

        Raises:
            ValueError: If the module name is already registered.
        """
        if name in self._modules:
            raise ValueError(f'Module {name} already registered in '
                             ' {self._category}.')
        self._modules[name] = module

    def get(self, name: str) -> Union[Type[Any], None]:
        """Retrieve a module based on its registered name.

        Args:
            name (str): The name of the module to retrieve.

        Returns:
            Union[Type[Any], None]: The registered module/class or None if not
                found.

        Raises:
            KeyError: If the module name is not registered.
        """
        if name not in self._modules:
            raise KeyError(f'Module {name} not found in {self._category}.')
        return self._modules[name]

    def __contains__(self, name: str) -> bool:
        """Check if a module name is registered.

        Args:
            name (str): The name of the module to check.

        Returns:
            bool: True if the module name is registered, False otherwise.
        """
        return name in self._modules

    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        return f'{self._category}: ' + ', '.join(self._modules.keys())
