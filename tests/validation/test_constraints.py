import pytest

from src.validation.constraints import (
    validate_order_status_transition,
    validate_integer_blocks,
    validate_price,
    validate_servings,
    ValidationError,
)


def test_valid_status_transition() -> None:
    """Test valid status transitions."""
    assert validate_order_status_transition('planning', 'ordered')
    assert validate_order_status_transition('ordered', 'delivered')
    assert validate_order_status_transition('delivered', 'reconciled')


def test_any_to_any_status_allowed() -> None:
    """Test any status can transition to any other."""
    assert validate_order_status_transition('reconciled', 'planning')
    assert validate_order_status_transition('planning', 'reconciled')


def test_invalid_status() -> None:
    """Test invalid status raises error."""
    with pytest.raises(ValidationError):
        validate_order_status_transition('planning', 'invalid_status')


def test_integer_blocks_valid() -> None:
    """Test integer blocks validation."""
    assert validate_integer_blocks(5.0, blocks_must_be_integer=1)
    assert validate_integer_blocks(5.5, blocks_must_be_integer=0)


def test_integer_blocks_fractional_rejected() -> None:
    """Test fractional blocks rejected when required."""
    with pytest.raises(ValidationError):
        validate_integer_blocks(5.5, blocks_must_be_integer=1)


def test_price_valid() -> None:
    """Test price validation."""
    assert validate_price(0.0)
    assert validate_price(2.99)
    assert validate_price(100.0)


def test_price_negative_rejected() -> None:
    """Test negative price rejected."""
    with pytest.raises(ValidationError):
        validate_price(-1.0)


def test_servings_valid() -> None:
    """Test servings validation."""
    assert validate_servings(0.5)
    assert validate_servings(1.0)
    assert validate_servings(100.0)


def test_servings_zero_rejected() -> None:
    """Test zero servings rejected."""
    with pytest.raises(ValidationError):
        validate_servings(0.0)


def test_servings_negative_rejected() -> None:
    """Test negative servings rejected."""
    with pytest.raises(ValidationError):
        validate_servings(-1.0)
