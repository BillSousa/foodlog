from dataclasses import dataclass


@dataclass
class Nutrient:
    """FDA reference daily values nutrient."""

    nutrient_id: int | None = None
    nutrient_name: str = ""
    dv_amount: float = 0.0
    is_tracked: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'nutrient_id': self.nutrient_id,
            'nutrient_name': self.nutrient_name,
            'dv_amount': self.dv_amount,
            'is_tracked': self.is_tracked,
        }
