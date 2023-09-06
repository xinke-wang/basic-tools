from typing import Any, Callable, Optional, Type, TypeVar, Union

T = TypeVar('T')


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

    def register(self,
                 name: Optional[str] = None) -> Callable[[Type[T]], Type[T]]:
        """Register a module with a given name.

        This method can be used as a decorator.

        Args:
            name (Optional[str]): The name to register the module under.
                If None, use the name of the module to be registered.

        Returns:
            Callable[[Type[T]], Type[T]]: A decorator for registering the
                module.

        Examples:
            >>> @registry.register('example')
            ... class ExampleModule:
            ...     pass

            >>> registry.register('example', ExampleModule)
        """

        def _register(module: Type[T]) -> Type[T]:
            _name = name
            if _name is None:
                _name = module.__name__
            if _name in self._modules:
                raise ValueError(
                    f'Module {_name} already registered in {self._category}.')
            self._modules[_name] = module
            return module

        return _register

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
