import pytest

from foodlog.validation.constraints import (
    validate_order_status_transition,
    validate_integer_blocks,
    validate_price,
    validate_servings,
    validate_order_editable,
    ValidationError,
)


def test_valid_status_transition() -> None:
    """Test valid status transitions."""
    assert validate_order_status_transition('planning', 'ordered') is True
    assert validate_order_status_transition('ordered', 'delivered') is True
    assert validate_order_status_transition('delivered', 'reconciled') is True


def test_any_to_any_status_allowed() -> None:
    """Test any status can transition to any other."""
    assert validate_order_status_transition('reconciled', 'planning') is True
    assert validate_order_status_transition('planning', 'reconciled') is True


def test_invalid_status() -> None:
    """Test invalid status raises error."""
    with pytest.raises(ValidationError):
        validate_order_status_transition('planning', 'invalid_status')


def test_invalid_current_status() -> None:
    """Test invalid current_status raises error."""
    with pytest.raises(ValidationError):
        validate_order_status_transition('invalid_status', 'planning')


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


def test_order_editable_valid_statuses() -> None:
    """Test editable statuses allow editing."""
    assert validate_order_editable('planning') is True
    assert validate_order_editable('ordered') is True
    assert validate_order_editable('delivered') is True


def test_order_editable_reconciled_rejected() -> None:
    """Test reconciled status blocks editing."""
    with pytest.raises(ValidationError):
        validate_order_editable('reconciled')


def test_order_editable_invalid_status_rejected() -> None:
    """Test invalid status raises error."""
    with pytest.raises(ValidationError):
        validate_order_editable('invalid_status')
