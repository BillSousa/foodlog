"""Tests for nutrient metadata helpers."""

from foodlog.nutrients.metadata import (
    is_dv_percent_nutrient,
    get_nutrient_unit,
    get_nutrient_dv_amount,
)


def test_dv_percent_nutrients() -> None:
    """Test identification of %DV-based nutrients."""
    # Vitamins should be %DV
    assert is_dv_percent_nutrient("Vitamin D") is True
    assert is_dv_percent_nutrient("Vitamin A") is True
    assert is_dv_percent_nutrient("Vitamin C") is True
    assert is_dv_percent_nutrient("Calcium") is True
    assert is_dv_percent_nutrient("Iron") is True


def test_mass_nutrients_not_dv_percent() -> None:
    """Test identification of mass-based nutrients."""
    # Macros and other mass values should not be %DV
    assert is_dv_percent_nutrient("Calories") is False
    assert is_dv_percent_nutrient("Total Fat") is False
    assert is_dv_percent_nutrient("Protein") is False
    assert is_dv_percent_nutrient("Sodium") is False


def test_nutrient_unit_dv_shows_percent() -> None:
    """Test that %DV nutrients show % as unit."""
    assert get_nutrient_unit("Vitamin D") == "%"
    assert get_nutrient_unit("Vitamin A") == "%"
    assert get_nutrient_unit("Calcium") == "%"


def test_nutrient_unit_mass_shows_actual_unit() -> None:
    """Test that mass nutrients show their actual unit."""
    assert get_nutrient_unit("Calories") == "kcal"
    assert get_nutrient_unit("Total Fat") == "g"
    assert get_nutrient_unit("Sodium") == "mcg"
    assert get_nutrient_unit("Protein") == "g"


def test_get_nutrient_dv_amount() -> None:
    """Test retrieval of daily value amounts."""
    # Vitamin A DV should be 900 mcg
    assert get_nutrient_dv_amount("Vitamin A") == 900.0

    # Vitamin D DV should be 20 mcg
    assert get_nutrient_dv_amount("Vitamin D") == 20.0

    # Calcium DV should be 1300000 mcg
    assert get_nutrient_dv_amount("Calcium") == 1300000.0

    # Sodium is stored in mcg (2300000)
    assert get_nutrient_dv_amount("Sodium") == 2300000.0


def test_unknown_nutrient_returns_none() -> None:
    """Test that unknown nutrients return None."""
    assert is_dv_percent_nutrient("Unknown Nutrient") is False
    assert get_nutrient_unit("Unknown Nutrient") == "?"
    assert get_nutrient_dv_amount("Unknown Nutrient") is None
