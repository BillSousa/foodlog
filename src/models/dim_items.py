from dataclasses import dataclass

from typing import (
    Literal,
    Optional
)


@dataclass
class Item:
    """Food item with nutrition and pricing (SCD2 versioning on nutrition)."""

    item_id: Optional[int] = None
    name_id: int = 0
    category_id: Optional[int] = None
    price: float = 0.0
    servings_per_block: float = 0.0
    units: Optional[Literal["units", "g", "kg", "oz", "lb", "mL", "L", "fl oz", "tsp", "Tbsp", "cup", "pint", "quart", "gal"]] = None
    container_size: float = 0.0
    serving_size: float = 0.0
    blocks_must_be_integer: int = 0
    active: int = 1
    glycemic_index: Optional[int] = None
    ratio1: float = 0.0
    ratio2: float = 0.0
    calories: float = 0.0
    total_fat_g: float = 0.0
    saturated_fat_g: float = 0.0
    trans_fat_g: float = 0.0
    cholesterol_mcg: float = 0.0
    sodium_mcg: float = 0.0
    total_carbs_g: float = 0.0
    dietary_fiber_g: float = 0.0
    total_sugars_g: float = 0.0
    added_sugars_g: float = 0.0
    protein_g: float = 0.0
    vitamin_d_mcg: float = 0.0
    calcium_mcg: float = 0.0
    iron_mcg: float = 0.0
    potassium_mcg: float = 0.0
    vitamin_a_mcg: float = 0.0
    vitamin_c_mcg: float = 0.0
    vitamin_e_mcg: float = 0.0
    vitamin_k_mcg: float = 0.0
    thiamin_mcg: float = 0.0
    riboflavin_mcg: float = 0.0
    niacin_mcg: float = 0.0
    vitamin_b6_mcg: float = 0.0
    folate_mcg: float = 0.0
    vitamin_b12_mcg: float = 0.0
    biotin_mcg: float = 0.0
    pantothenic_acid_mcg: float = 0.0
    phosphorus_mcg: float = 0.0
    iodine_mcg: float = 0.0
    magnesium_mcg: float = 0.0
    zinc_mcg: float = 0.0
    selenium_mcg: float = 0.0
    copper_mcg: float = 0.0
    manganese_mcg: float = 0.0
    chromium_mcg: float = 0.0
    molybdenum_mcg: float = 0.0
    chloride_mcg: float = 0.0
    ethanol_g: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {k: v for k, v in self.__dict__.items()}
