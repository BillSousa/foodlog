"""Nutrient metadata and helpers."""

from foodlog.database.seed_reference_data import NUTRIENTS


def is_dv_percent_nutrient(nutrient_name: str) -> bool:
    """
    Check if a nutrient uses %DV entry (vs. absolute mass).

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        True if user enters %DV, False if user enters absolute mass
    """
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
    for name, unit, dv, tracked, is_dv_percent in NUTRIENTS:
        if name == nutrient_name:
            return "%" if is_dv_percent else unit
    return "?"


def get_nutrient_dv_amount(nutrient_name: str) -> float | None:
    """
    Get the daily value (for %DV conversion).

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        Daily value in mcg, or None if not found
    """
    for name, unit, dv, tracked, is_dv_percent in NUTRIENTS:
        if name == nutrient_name:
            return dv
    return None
