"""Tests for %DV nutrition value conversion."""

import pytest

from src.conversion.nutrition_converter import (
    convert_nutrition_for_storage,
    get_column_name,
)
from src.conversion.units import dv_percent_to_mcg


def test_mass_nutrient_stored_as_entered() -> None:
    """Test that mass-based nutrients are stored as entered."""
    # Sodium is mass-based (stored as mg)
    result = convert_nutrition_for_storage("Sodium", 1000.0)
    assert result == 1000.0

    # Calories is mass-based
    result = convert_nutrition_for_storage("Calories", 150.0)
    assert result == 150.0

    # Total Fat is mass-based
    result = convert_nutrition_for_storage("Total Fat", 10.0)
    assert result == 10.0


def test_dv_percent_nutrient_converts_to_mcg() -> None:
    """Test that %DV nutrients are converted to mcg."""
    # Vitamin A: DV = 900 mcg, user enters 50%
    result = convert_nutrition_for_storage("Vitamin A", 50.0)
    expected = dv_percent_to_mcg(50.0, 900.0)
    assert result == expected
    assert result == 450.0  # (50 / 100) * 900

    # Vitamin D: DV = 20 mcg, user enters 100%
    result = convert_nutrition_for_storage("Vitamin D", 100.0)
    expected = dv_percent_to_mcg(100.0, 20.0)
    assert result == expected
    assert result == 20.0

    # Calcium: DV = 1300000 mcg, user enters 25%
    result = convert_nutrition_for_storage("Calcium", 25.0)
    expected = dv_percent_to_mcg(25.0, 1300000.0)
    assert result == expected
    assert result == 325000.0


def test_dv_zero_percent_returns_zero() -> None:
    """Test that 0% DV nutrients return 0."""
    result = convert_nutrition_for_storage("Vitamin A", 0.0)
    assert result == 0.0


def test_column_name_mapping_mass_nutrients() -> None:
    """Test nutrient to column name mapping for mass nutrients."""
    assert get_column_name("Calories") == "calories"
    assert get_column_name("Total Fat") == "total_fat_g"
    assert get_column_name("Sodium") == "sodium_mcg"
    assert get_column_name("Protein") == "protein_g"
    assert get_column_name("Cholesterol") == "cholesterol_mcg"


def test_column_name_mapping_dv_nutrients() -> None:
    """Test nutrient to column name mapping for %DV nutrients."""
    assert get_column_name("Vitamin D") == "vitamin_d_mcg"
    assert get_column_name("Vitamin A") == "vitamin_a_mcg"
    assert get_column_name("Calcium") == "calcium_mcg"
    assert get_column_name("Iron") == "iron_mcg"
    assert get_column_name("Vitamin K") == "vitamin_k_mcg"


def test_column_name_unknown_nutrient_returns_none() -> None:
    """Test that unknown nutrient names return None."""
    assert get_column_name("Unknown Nutrient") is None
    assert get_column_name("") is None


def test_all_nutrients_have_column_names() -> None:
    """Test that all seeded nutrients have column name mappings."""
    from src.database.seed_reference_data import NUTRIENTS

    for name, unit, dv, tracked, is_dv_percent in NUTRIENTS:
        column = get_column_name(name)
        assert column is not None, f"No column mapping for {name}"


def test_vitamin_d_conversion_matches_spec() -> None:
    """Test Vitamin D conversion per SPEC.md example."""
    # User enters 100% (entire daily value on label)
    # Should convert to the actual mcg amount
    result = convert_nutrition_for_storage("Vitamin D", 100.0)
    # Vitamin D DV is 20 mcg
    assert result == 20.0

    # User enters 50%
    result = convert_nutrition_for_storage("Vitamin D", 50.0)
    assert result == 10.0


def test_percent_dv_never_stored_directly() -> None:
    """
    Critical test: %DV values are NEVER stored directly in dim_items.

    They are converted to mcg at save time. This ensures historical
    consistency even if FDA daily values change (as they did in 2016).
    """
    # When user enters "25%" for Calcium
    # We should NOT store 25
    # We should store the converted mcg value
    result = convert_nutrition_for_storage("Calcium", 25.0)
    assert result != 25.0
    assert result == 325000.0  # 25% of 1,300,000 mcg DV
