from pytest import Subtests
import pytest
from app.lib.type_registry import TypeRegistry


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
