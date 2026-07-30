from dataclasses import dataclass


@dataclass
class Order:
    """Order fact table - header-level aggregates and metadata."""

    order_id: int | None = None
    order_date: str = ""
    is_delivery: int = 0
    status: str = "planning"
    delivery_charge: float = 0.0
    tip: float = 0.0
    tax: float = 0.0
    order_level_coupon: float = 0.0
    total_net_cost: float = 0.0
    total_calories: float = 0.0
    total_protein_g: float = 0.0
    total_carbs_g: float = 0.0
    total_fat_g: float = 0.0
    total_sodium_mg: float = 0.0
    ratio1: float = 0.0
    ratio2: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {k: v for k, v in self.__dict__.items()}
