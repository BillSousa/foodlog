"""Nutrient metadata and helpers."""

# TODO: "NUTRIENTS" NEEDS TO COME OUT.
from foodlog.database.seed_reference_data import NUTRIENTS


def is_dv_percent_nutrient(nutrient_name: str) -> bool:
    """
    Check if a nutrient uses %DV entry (vs. absolute mass).

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        True if user enters %DV, False if user enters absolute mass    
    """

    # TODO: "NUTRIENTS" NEEDS TO COME OUT.
    # THIS FUNCTION NEEDS TO CHANGE TO PULL FROM ref_daily_values.nutrient_entry_unit.
    for name, unit, dv, tracked, is_dv_percent in NUTRIENTS:
        if name == nutrient_name:
            return is_dv_percent
    return False


def get_nutrient_unit(nutrient_name: str) -> str:
    """
    Get the display unit for a nutrient.

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        Unit string (g, mg, mcg, kcal, %)
    """

    # TODO: "NUTRIENTS" NEEDS TO COME OUT.
    # THIS FUNCTION NEEDS TO CHANGE TO PULL FROM ref_daily_values.nutrient_entry_unit.
    # THIS FUNCTION MAY BE MORE APPROPRIATELY NAMED `get_nutrient_entry_unit`.
    for name, unit, dv, tracked, is_dv_percent in NUTRIENTS:
        if name == nutrient_name:
            return "%" if is_dv_percent else unit
    return "?"


# TODO: NEED TO CREATE A get_nutrient_dim_items_unit() FUNCTION.
# THIS FUNCTION NEEDS TO PULL FROM ref_daily_values.nutrient_dim_items_unit.


def get_nutrient_dv_amount(nutrient_name: str) -> float | None:
    """
    Get the daily value (for %DV conversion).

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        Daily value in mcg, or None if not found
    """

    # TODO: "NUTRIENTS" NEEDS TO COME OUT, USE ref_daily_values.dv_amount
    for name, unit, dv, tracked, is_dv_percent in NUTRIENTS:
        if name == nutrient_name:
            return dv
    return None
