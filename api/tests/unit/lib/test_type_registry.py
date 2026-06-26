from abc import abstractmethod
from typing import Protocol, reveal_type
from pytest import Subtests
import pytest
from app.lib.type_registry import TraitRegistry, TypeCallbackRegistry, TypeRegistry


def test_type_registry(subtests: Subtests):

    class Foo:
        pass

    class Bar(Foo):
        pass

    class Baz(Bar):
        pass

    class Quux:
        pass

    registry = TypeRegistry[str]()
    registry.set(Foo, "FOO")
    registry.set(Baz, "BAZ")

    with subtests.test("Get value for exact type"):
        assert registry.get(Foo) == "FOO"

    with subtests.test("Get value for subtype"):
        assert registry.get(Bar) == "FOO"

    with subtests.test("Get value for sub-sub-type with override"):
        assert registry.get(Baz) == "BAZ"

    with subtests.test("Get for missing  type"):
        with pytest.raises(KeyError):
            registry.get(Quux)


def test_method_registry(subtests):

    class Foo:
        name = "foo"

    class Bar(Foo):
        name = "bar"

    class Baz(Bar):
        name = "baz"

    registry = TypeCallbackRegistry[str]()

    @registry.declare(Foo)
    def some_method_for_foo(foo: Foo) -> str:
        return foo.name

    @registry.declare(Baz)
    def some_method_for_baz(baz: Baz) -> str:
        return "BAZZZ!"

    with subtests.test("Call method for exact type"):
        assert registry.call_method(Foo()) == "foo"

    with subtests.test("Call method for sub-type"):
        assert registry.call_method(Bar()) == "bar"

    with subtests.test("Call method for sub-sub-type with override"):
        assert registry.call_method(Baz()) == "BAZZZ!"


def test_trait_registry(subtests):

    class Foo:
        name = "foo"

    class Bar(Foo):
        name = "bar"

    class Baz(Bar):
        name = "baz"

    class GetName(Protocol):
        @abstractmethod
        def get_name(self) -> str:
            raise NotImplementedError

    GetNameTrait = TraitRegistry[GetName]()

    @GetNameTrait.impl(Foo)
    class GetNameForFoo(GetName):
        def __init__(self, foo: Foo):
            self._foo = foo

        def get_name(self):
            return self._foo.name

    @GetNameTrait.impl(Baz)
    class GetNameForBaz(GetName):
        def __init__(self, baz: Baz):
            self._baz = baz

        def get_name(self):
            return "BAZZZ!"

    with subtests.test("Use trait for exact type"):
        assert GetNameTrait(Foo()).get_name() == "foo"

    with subtests.test("Use trait for sub-type"):
        assert GetNameTrait(Bar()).get_name() == "bar"

    with subtests.test("Use trait for sub-sub-type with override"):
        assert GetNameTrait(Baz()).get_name() == "BAZZZ!"
