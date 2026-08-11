"""Nutrient metadata and helpers."""

from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


def _get_nutrient_row(nutrient_name: str):
    """Look up a nutrient's full row, or None if unknown."""
    return TrackedNutrientsRepository().get_by_name(nutrient_name)


def is_dv_percent_nutrient(nutrient_name: str) -> bool:
    """
    Check if a nutrient uses %DV entry (vs. absolute mass).

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        True if user enters %DV, False if user enters absolute mass
    """
    row = _get_nutrient_row(nutrient_name)
    return row is not None and row.nutrient_entry_unit == "%"


def get_nutrient_entry_unit(nutrient_name: str) -> str:
    """
    Get the unit the item create/edit GUI asks the user to enter.

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        Unit string (g, mg, mcg, kcal, %), or "?" if unknown
    """
    row = _get_nutrient_row(nutrient_name)
    return row.nutrient_entry_unit if row else "?"


def get_nutrient_fda_label_unit(nutrient_name: str) -> str:
    """
    Get the unit as printed on real FDA nutrition labels.

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        Unit string (g, mg, mcg, kcal), or "?" if unknown
    """
    row = _get_nutrient_row(nutrient_name)
    return row.nutrient_fda_label_unit if row else "?"


def get_nutrient_dim_items_unit(nutrient_name: str) -> str:
    """
    Get the unit a nutrient's value is stored in on dim_items.

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        Unit string (g, mcg, kcal), or "?" if unknown
    """
    row = _get_nutrient_row(nutrient_name)
    return row.nutrient_dim_items_unit if row else "?"


def get_nutrient_dv_amount(nutrient_name: str) -> float | None:
    """
    Get the daily value (for %DV conversion).

    Args:
        nutrient_name: Name of the nutrient

    Returns:
        Daily value in mcg, or None if not found
    """
    row = _get_nutrient_row(nutrient_name)
    return row.dv_amount if row else None
