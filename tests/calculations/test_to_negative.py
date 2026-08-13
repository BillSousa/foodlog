import pytest

from foodlog.calculations.to_negative import to_negative


@pytest.mark.parametrize("input_value,expected", [
    (0.5, -0.5),
    (-0.5, -0.5),
    (0, 0),
])
def test_to_negative(input_value: float, expected: float) -> None:
    """Test that to_negative forces values to be negative."""
    assert to_negative(input_value) == expected
