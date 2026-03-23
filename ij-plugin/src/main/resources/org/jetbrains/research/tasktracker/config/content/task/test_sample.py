import pytest
from sample import add, subtract, divide, is_even


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(10, 4) == 6


def test_divide():
    assert divide(10, 2) == 5.0


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(5, 0)


def test_is_even_true():
    assert is_even(4) is True


def test_is_even_false():
    assert is_even(7) is False