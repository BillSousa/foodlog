from dataclasses import dataclass


@dataclass
class OrderLine:
    """Order line item - per-item detail within an order."""

    line_id: int | None = None
    order_id: int = 0
    item_id: int = 0
    servings_ordered: float = 0.0
    actual_servings: float = 0.0
    stated_price: float = 0.0
    sale: float = 0.0
    discount: float = 0.0
    coupon: float = 0.0
    net_price: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {k: v for k, v in self.__dict__.items()}
