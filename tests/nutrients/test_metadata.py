"""Tests for nutrient metadata helpers."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.nutrients.metadata import (
    is_dv_percent_nutrient,
    get_nutrient_entry_unit,
    get_nutrient_fda_label_unit,
    get_nutrient_dim_items_unit,
    get_nutrient_dv_amount,
)
from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


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
        seed_reference_data(conn)
        conn.close()
    return db_path


def test_dv_percent_nutrients(test_db: Path) -> None:
    """Test identification of %DV-based nutrients."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert is_dv_percent_nutrient("Vitamin D") is True
        assert is_dv_percent_nutrient("Vitamin A") is True
        assert is_dv_percent_nutrient("Vitamin C") is True
        assert is_dv_percent_nutrient("Calcium") is True
        assert is_dv_percent_nutrient("Iron") is True


def test_mass_nutrients_not_dv_percent(test_db: Path) -> None:
    """Test identification of mass-based nutrients."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert is_dv_percent_nutrient("Calories") is False
        assert is_dv_percent_nutrient("Total Fat") is False
        assert is_dv_percent_nutrient("Protein") is False
        assert is_dv_percent_nutrient("Sodium") is False


def test_nutrient_entry_unit_dv_shows_percent(test_db: Path) -> None:
    """Test that %DV nutrients show % as entry unit."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert get_nutrient_entry_unit("Vitamin D") == "%"
        assert get_nutrient_entry_unit("Vitamin A") == "%"
        assert get_nutrient_entry_unit("Calcium") == "%"


def test_nutrient_entry_unit_mass_shows_actual_unit(test_db: Path) -> None:
    """Test that mass nutrients show their actual entry unit."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert get_nutrient_entry_unit("Calories") == "kcal"
        assert get_nutrient_entry_unit("Total Fat") == "g"
        assert get_nutrient_entry_unit("Sodium") == "mg"
        assert get_nutrient_entry_unit("Protein") == "g"


def test_get_nutrient_fda_label_unit(test_db: Path) -> None:
    """Test retrieval of FDA label units."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert get_nutrient_fda_label_unit("Vitamin D") == "mcg"
        assert get_nutrient_fda_label_unit("Sodium") == "mg"
        assert get_nutrient_fda_label_unit("Calories") == "kcal"
        assert get_nutrient_fda_label_unit("Vitamin A") == "mcg"


def test_get_nutrient_dim_items_unit(test_db: Path) -> None:
    """Test retrieval of dim_items storage units."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert get_nutrient_dim_items_unit("Vitamin D") == "mcg"
        assert get_nutrient_dim_items_unit("Sodium") == "mcg"
        assert get_nutrient_dim_items_unit("Calories") == "kcal"
        assert get_nutrient_dim_items_unit("Calcium") == "mcg"


def test_get_nutrient_dv_amount(test_db: Path) -> None:
    """Test retrieval of daily value amounts."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert get_nutrient_dv_amount("Vitamin A") == 900.0
        assert get_nutrient_dv_amount("Vitamin D") == 20.0
        assert get_nutrient_dv_amount("Calcium") == 1300000.0
        assert get_nutrient_dv_amount("Sodium") == 2300000.0


def test_unknown_nutrient_returns_none(test_db: Path) -> None:
    """Test that unknown nutrients return appropriate defaults."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        assert is_dv_percent_nutrient("Unknown Nutrient") is False
        assert get_nutrient_entry_unit("Unknown Nutrient") == "?"
        assert get_nutrient_fda_label_unit("Unknown Nutrient") == "?"
        assert get_nutrient_dim_items_unit("Unknown Nutrient") == "?"
        assert get_nutrient_dv_amount("Unknown Nutrient") is None


def test_dv_amount_edit_reflected_in_conversion(test_db: Path) -> None:
    """Test that edits to dv_amount via repo are reflected in metadata."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()
        sodium = next(n for n in all_nutrients if n.nutrient_name == "Sodium")

        original_dv = get_nutrient_dv_amount("Sodium")
        assert original_dv == 2300000.0

        repo.update_nutrient(
            sodium.nutrient_id,
            "Sodium",
            2400000.0,
            0
        )

        updated_dv = get_nutrient_dv_amount("Sodium")
        assert updated_dv == 2400000.0
