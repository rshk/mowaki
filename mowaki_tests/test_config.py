import dataclasses
from dataclasses import dataclass

import pytest

from mowaki.config import create_config_from_env


class Test_dataclass_field_parsing:
    def test_field_with_no_default_is_required(self):
        @dataclass
        class SomeObject:
            somefield: str

        fields = dataclasses.fields(SomeObject)
        [field] = fields
        assert field.name == "somefield"
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
        assert field.type is str


class Test_load_string_config:
    def test_required_string_is_loaded(self):
        @dataclass
        class MyConfig:
            mystring: str

        env = {"MYSTRING": "Some value"}
        result = create_config_from_env(MyConfig, env)

        assert isinstance(result, MyConfig)
        assert result.mystring == "Some value"

    def test_required_string_cannot_be_missing(self):
        @dataclass
        class MyConfig:
            mystring: str

        env = {}
        with pytest.raises(KeyError):
            create_config_from_env(MyConfig, env)

    def test_omitted_optional_string_uses_default(self):
        @dataclass
        class MyConfig:
            mystring: str = "Default value"

        result = create_config_from_env(MyConfig, {})

        assert isinstance(result, MyConfig)
        assert result.mystring == "Default value"

    def test_omitted_optional_string_uses_default_factory(self):
        @dataclass
        class MyConfig:
            mystring: str = dataclasses.field(default_factory=lambda: "Default value")

        result = create_config_from_env(MyConfig, {})

        assert isinstance(result, MyConfig)
        assert result.mystring == "Default value"


class Test_load_int_config:
    def test_int_value_is_loaded(self):
        @dataclass
        class MyConfig:
            myint: int

        env = {"MYINT": "32"}
        result = create_config_from_env(MyConfig, env)

        assert isinstance(result, MyConfig)
        assert result.myint == 32


class Test_load_bool_config:
    @pytest.mark.parametrize("raw,expected", [
        ("TRUE", True),
        ("FALSE", False),
        ("yes", True),
        ("no", False),
        ("1", True),
        ("0", False),
        ("", False),
    ])
    def test_bool_value_is_loaded(self, raw, expected):
        @dataclass
        class MyConfig:
            mybool: bool

        env = {"MYBOOL": raw}
        result = create_config_from_env(MyConfig, env)

        assert isinstance(result, MyConfig)
        assert result.mybool is expected
