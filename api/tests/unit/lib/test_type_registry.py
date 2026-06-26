from pytest import Subtests
import pytest
from app.lib.type_registry import TypeCallbackRegistry, TypeRegistry


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
