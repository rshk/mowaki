"""
Registry to hold values associated to a type.

Values will be resolved according to the type MRO.
"""

from typing import Callable, Type


class TypeRegistry[T]:
    _registry: dict[Type, T]

    def __init__(self):
        self._registry = {}

    def set(self, type_: Type, value: T):
        self._registry[type_] = value

    def get(self, type_: Type) -> T:
        for subtype in type_.mro():
            try:
                return self._registry[subtype]
            except KeyError:
                pass
        raise KeyError(f"No entry found for {type_}")


class TypeCallbackRegistry[T: Callable](TypeRegistry[T]):
    """
    Specialized registry to hold callables.

    This can be used to store "external" methods on a type, sort-of
    like Rust traits.
    """

    def declare(self, type_: Type) -> Callable[[T], None]:
        def decorator(fn: T):
            self.set(type_, fn)

        return decorator
