"""Convert nutrition values from user input to stored format."""

from src.conversion.units import dv_percent_to_mcg
from src.nutrients.metadata import (
    is_dv_percent_nutrient,
    get_nutrient_dv_amount,
)

# Map nutrient display names to dim_items attribute names
NUTRIENT_TO_COLUMN_MAP = {
    "Calories": "calories",
    "Total Fat": "total_fat_g",
    "Saturated Fat": "saturated_fat_g",
    "Trans Fat": "trans_fat_g",
    "Cholesterol": "cholesterol_mg",
    "Sodium": "sodium_mg",
    "Total Carbohydrate": "total_carbs_g",
    "Dietary Fiber": "dietary_fiber_g",
    "Total Sugars": "total_sugars_g",
    "Added Sugars": "added_sugars_g",
    "Protein": "protein_g",
    "Vitamin D": "vitamin_d_mcg",
    "Calcium": "calcium_mcg",
    "Iron": "iron_mcg",
    "Potassium": "potassium_mcg",
    "Vitamin A": "vitamin_a_mcg",
    "Vitamin C": "vitamin_c_mcg",
    "Vitamin E": "vitamin_e_mcg",
    "Vitamin K": "vitamin_k_mcg",
    "Thiamin (Vitamin B1)": "thiamin_mcg",
    "Riboflavin (Vitamin B2)": "riboflavin_mcg",
    "Niacin (Vitamin B3)": "niacin_mcg",
    "Vitamin B6": "vitamin_b6_mcg",
    "Folate": "folate_mcg",
    "Vitamin B12": "vitamin_b12_mcg",
    "Biotin": "biotin_mcg",
    "Pantothenic Acid": "pantothenic_acid_mcg",
    "Phosphorus": "phosphorus_mcg",
    "Iodine": "iodine_mcg",
    "Magnesium": "magnesium_mcg",
    "Zinc": "zinc_mcg",
    "Selenium": "selenium_mcg",
    "Copper": "copper_mcg",
    "Manganese": "manganese_mcg",
    "Chromium": "chromium_mcg",
    "Molybdenum": "molybdenum_mcg",
    "Chloride": "chloride_mcg",
    "Choline": "choline_mcg",
    "Ethanol": "ethanol_g",
}


def convert_nutrition_for_storage(
    nutrient_name: str, user_value: float
) -> float:
    """
    Convert nutrition value from user input to storage format.

    For %DV nutrients: user enters percent, convert to mcg using daily value.
    For mass nutrients: user enters the value directly, store as-is.

    Args:
        nutrient_name: Name of the nutrient
        user_value: Value entered by user

    Returns:
        Value to store in dim_items (in mcg for %DV nutrients, original unit for others)
    """
    if not is_dv_percent_nutrient(nutrient_name):
        # Mass-based nutrient: store as entered
        return user_value

    # %DV nutrient: convert percent to mcg
    dv_amount = get_nutrient_dv_amount(nutrient_name)
    if dv_amount is None or dv_amount == 0:
        # No daily value defined
        return 0.0

    return dv_percent_to_mcg(user_value, dv_amount)


def get_column_name(nutrient_name: str) -> str | None:
    """
    Get the dim_items column name for a nutrient.

    Args:
        nutrient_name: Display name of the nutrient

    Returns:
        Column name in dim_items, or None if not found
    """
    return NUTRIENT_TO_COLUMN_MAP.get(nutrient_name)
