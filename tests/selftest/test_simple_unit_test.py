import pytest


def add_numbers(a, b):
    return a + b


def divide_numbers(a, b):
    return a / b


def test_add_two_numbers():
    assert add_numbers(1, 2) == 3


def test_add_number_to_string():
    with pytest.raises(TypeError) as exc:
        add_numbers(1, "a")
    assert str(exc.value) == "unsupported operand type(s) for +: 'int' and 'str'"


def test_divide_two_numbers():
    assert divide_numbers(1, 2) == 0.5


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError) as exc:
        divide_numbers(1, 0)
    assert str(exc.value) == "division by zero"
