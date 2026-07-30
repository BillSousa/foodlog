from src.calculations.on_hand import calculate_on_hand
from src.database.connection import get_connection


class ValidationError(Exception):
    """Raised when a business rule constraint is violated."""

    pass


def validate_order_status_transition(current_status: str,
                                     new_status: str) -> bool:
    """
    Validate order status transitions.

    Status must be one of: planning, ordered, delivered, reconciled.
    Any status can transition to any other (soft lock only).

    Args:
        current_status: Current order status
        new_status: Desired new status

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If new_status is invalid
    """
    valid_statuses = {'planning', 'ordered', 'delivered', 'reconciled'}

    if new_status not in valid_statuses:
        raise ValidationError(
            f"Invalid status '{new_status}'. "
            f"Must be one of: {valid_statuses}"
        )

    return True


def validate_consumption_on_hand(item_id: int,
                                 servings_to_consume: float) -> bool:
    """
    Hard block: reject consumption if it would make on_hand negative.

    Args:
        item_id: Item being consumed
        servings_to_consume: Servings to consume now

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If would cause on_hand < 0
    """
    on_hand = calculate_on_hand(item_id)
    new_on_hand = on_hand - servings_to_consume

    if new_on_hand < 0:
        raise ValidationError(
            f"Cannot consume {servings_to_consume} servings. "
            f"On hand: {on_hand}, would result in {new_on_hand}"
        )

    return True


def validate_integer_blocks(blocks: float, blocks_must_be_integer: int) -> bool:
    """
    Reject fractional blocks if item requires integer-only.

    Args:
        blocks: Number of blocks entered
        blocks_must_be_integer: Flag (0=allow fractional, 1=integer only)

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If fractional and flag is set
    """
    if blocks_must_be_integer and blocks != int(blocks):
        raise ValidationError(
            f"This item requires integer blocks. "
            f"Got: {blocks}"
        )

    return True


def validate_price(price: float) -> bool:
    """
    Validate price is non-negative.

    Args:
        price: Price value

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If price < 0
    """
    if price < 0:
        raise ValidationError(f"Price cannot be negative: {price}")

    return True


def validate_servings(servings: float) -> bool:
    """
    Validate servings is positive.

    Args:
        servings: Servings value

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If servings <= 0
    """
    if servings <= 0:
        raise ValidationError(f"Servings must be positive: {servings}")

    return True
