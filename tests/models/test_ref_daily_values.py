"""Tests for Nutrient model."""

import pytest

from foodlog.models.ref_daily_values import Nutrient


def test_nutrient_defaults() -> None:
    """Test Nutrient dataclass default values."""
    nutrient = Nutrient()
    assert nutrient.nutrient_id is None
    assert nutrient.nutrient_name == ""
    assert nutrient.nutrient_fda_label_unit == ""
    assert nutrient.nutrient_entry_unit == ""
    assert nutrient.nutrient_dim_items_unit == ""
    assert nutrient.dv_amount == 0.0
    assert nutrient.is_tracked == 0


def test_nutrient_custom_values() -> None:
    """Test Nutrient with custom values."""
    nutrient = Nutrient(
        nutrient_id=1,
        nutrient_name="Sodium",
        nutrient_fda_label_unit="mg",
        nutrient_entry_unit="mg",
        nutrient_dim_items_unit="mcg",
        dv_amount=2300000.0,
        is_tracked=1
    )
    assert nutrient.nutrient_id == 1
    assert nutrient.nutrient_name == "Sodium"
    assert nutrient.nutrient_fda_label_unit == "mg"
    assert nutrient.nutrient_entry_unit == "mg"
    assert nutrient.nutrient_dim_items_unit == "mcg"
    assert nutrient.dv_amount == 2300000.0
    assert nutrient.is_tracked == 1


def test_nutrient_to_dict_defaults() -> None:
    """Test to_dict() with default values."""
    nutrient = Nutrient()
    result = nutrient.to_dict()
    assert result == {
        'nutrient_id': None,
        'nutrient_name': "",
        'nutrient_fda_label_unit': "",
        'nutrient_entry_unit': "",
        'nutrient_dim_items_unit': "",
        'dv_amount': 0.0,
        'is_tracked': 0,
    }


def test_nutrient_to_dict_custom_values() -> None:
    """Test to_dict() with custom values."""
    nutrient = Nutrient(
        nutrient_id=5,
        nutrient_name="Vitamin D",
        nutrient_fda_label_unit="mcg",
        nutrient_entry_unit="%",
        nutrient_dim_items_unit="mcg",
        dv_amount=20.0,
        is_tracked=1
    )
    result = nutrient.to_dict()
    assert result == {
        'nutrient_id': 5,
        'nutrient_name': "Vitamin D",
        'nutrient_fda_label_unit': "mcg",
        'nutrient_entry_unit': "%",
        'nutrient_dim_items_unit': "mcg",
        'dv_amount': 20.0,
        'is_tracked': 1,
    }
