from dataclasses import dataclass


@dataclass
class Nutrient:
    """FDA reference daily values nutrient."""

    nutrient_id: int | None = None
    nutrient_name: str = ""
    nutrient_fda_label_unit: str = ""
    nutrient_entry_unit: str = ""
    nutrient_dim_items_unit: str = ""
    dv_amount: float = 0.0
    is_tracked: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'nutrient_id': self.nutrient_id,
            'nutrient_name': self.nutrient_name,
            'nutrient_fda_label_unit': self.nutrient_fda_label_unit,
            'nutrient_entry_unit': self.nutrient_entry_unit,
            'nutrient_dim_items_unit': self.nutrient_dim_items_unit,
            'dv_amount': self.dv_amount,
            'is_tracked': self.is_tracked,
        }
