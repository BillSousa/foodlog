"""Tests for %DV nutrition value conversion."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.conversion.nutrition_converter import (
    convert_nutrition_for_storage,
    convert_nutrition_for_display,
    get_column_name,
)
from foodlog.conversion.units import dv_percent_to_mcg
from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data


@pytest.fixture
def test_db() -> Path:
    """Create temp test database."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test.db"
    with patch(
        "foodlog.database.connection.get_database_path", return_value=db_path
    ):
        conn = get_connection()
        create_schema(conn)
        migrate_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


def test_mg_to_mcg_conversion(test_db: Path) -> None:
    """Test that mg-entry nutrients are converted to mcg for storage."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # Sodium: user enters in mg, stored in mcg
        result = convert_nutrition_for_storage("Sodium", 1000.0)
        assert result == 1_000_000.0

        # Cholesterol: user enters in mg, stored in mcg
        result = convert_nutrition_for_storage("Cholesterol", 300.0)
        assert result == 300_000.0


def test_nutrients_without_conversion_stored_as_entered(test_db: Path) -> None:
    """Test that nutrients without unit conversion are stored as entered."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # Calories (kcal, no conversion)
        result = convert_nutrition_for_storage("Calories", 150.0)
        assert result == 150.0

        # Total Fat (g, no conversion)
        result = convert_nutrition_for_storage("Total Fat", 10.0)
        assert result == 10.0


def test_dv_percent_nutrient_converts_to_mcg(test_db: Path) -> None:
    """Test that %DV nutrients are converted to mcg."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
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


def test_dv_zero_percent_returns_zero(test_db: Path) -> None:
    """Test that 0% DV nutrients return 0."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
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


def test_all_nutrients_have_column_names(test_db: Path) -> None:
    """Test that all seeded nutrients have column name mappings."""
    from foodlog.repository.tracked_nutrients_repository import (
        TrackedNutrientsRepository,
    )

    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        for nutrient in TrackedNutrientsRepository().list_all_nutrients():
            column = get_column_name(nutrient.nutrient_name)
            assert (
                column is not None
            ), f"No column mapping for {nutrient.nutrient_name}"


def test_vitamin_d_conversion_matches_spec(test_db: Path) -> None:
    """Test Vitamin D conversion per SPEC.md example."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # User enters 100% (entire daily value on label)
        # Should convert to the actual mcg amount
        result = convert_nutrition_for_storage("Vitamin D", 100.0)
        # Vitamin D DV is 20 mcg
        assert result == 20.0

        # User enters 50%
        result = convert_nutrition_for_storage("Vitamin D", 50.0)
        assert result == 10.0


def test_percent_dv_never_stored_directly(test_db: Path) -> None:
    """
    Critical test: %DV values are NEVER stored directly in dim_items.

    They are converted to mcg at save time. This ensures historical
    consistency even if FDA daily values change (as they did in 2016).
    """
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # When user enters "25%" for Calcium
        # We should NOT store 25
        # We should store the converted mcg value
        result = convert_nutrition_for_storage("Calcium", 25.0)
        assert result != 25.0
        assert result == 325000.0  # 25% of 1,300,000 mcg DV


def test_mcg_to_mg_display_conversion(test_db: Path) -> None:
    """Test that mcg-storage nutrients are converted to mg for display."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # Sodium: stored in mcg, displayed in mg
        result = convert_nutrition_for_display("Sodium", 1_000_000.0)
        assert result == 1000.0

        # Cholesterol: stored in mcg, displayed in mg
        result = convert_nutrition_for_display("Cholesterol", 300_000.0)
        assert result == 300.0


def test_nutrients_without_conversion_displayed_as_stored(
    test_db: Path,
) -> None:
    """Test that nutrients without unit conversion display as stored."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # Calories (kcal, no conversion)
        result = convert_nutrition_for_display("Calories", 150.0)
        assert result == 150.0

        # Total Fat (g, no conversion)
        result = convert_nutrition_for_display("Total Fat", 10.0)
        assert result == 10.0


def test_dv_percent_nutrient_converts_from_mcg(test_db: Path) -> None:
    """Test that %DV nutrients are converted from mcg to percent."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # Vitamin A: DV = 900 mcg, stored 450 mcg should display as 50%
        result = convert_nutrition_for_display("Vitamin A", 450.0)
        assert result == 50.0

        # Vitamin D: DV = 20 mcg, stored 20 mcg should display as 100%
        result = convert_nutrition_for_display("Vitamin D", 20.0)
        assert result == 100.0

        # Calcium: DV = 1300000 mcg, stored 325000 mcg should display as 25%
        result = convert_nutrition_for_display("Calcium", 325000.0)
        assert result == 25.0


def test_dv_zero_mcg_returns_zero_percent(test_db: Path) -> None:
    """Test that 0 mcg DV nutrients display as 0%."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        result = convert_nutrition_for_display("Vitamin A", 0.0)
        assert result == 0.0


def test_roundtrip_conversion_mass_nutrients(test_db: Path) -> None:
    """Test that convert_for_storage and convert_for_display are inverses."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # For Sodium: mg -> mcg -> mg
        original = 1500.0
        stored = convert_nutrition_for_storage("Sodium", original)
        displayed = convert_nutrition_for_display("Sodium", stored)
        assert displayed == original

        # For Cholesterol: mg -> mcg -> mg
        original = 200.0
        stored = convert_nutrition_for_storage("Cholesterol", original)
        displayed = convert_nutrition_for_display("Cholesterol", stored)
        assert displayed == original


def test_roundtrip_conversion_dv_nutrients(test_db: Path) -> None:
    """Test that convert_for_storage and convert_for_display are inverses."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # For Vitamin A: % -> mcg -> %
        original = 75.0
        stored = convert_nutrition_for_storage("Vitamin A", original)
        displayed = convert_nutrition_for_display("Vitamin A", stored)
        assert abs(displayed - original) < 0.01  # Allow for rounding

        # For Vitamin D: % -> mcg -> %
        original = 50.0
        stored = convert_nutrition_for_storage("Vitamin D", original)
        displayed = convert_nutrition_for_display("Vitamin D", stored)
        assert abs(displayed - original) < 0.01
