"""Tests for TrackedNutrientsRepository."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)
from foodlog.models.ref_daily_values import Nutrient


@pytest.fixture
def test_db() -> Path:
    """Create a temporary test database with schema and seed data."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test_foodlog.db"
    with patch(
        "foodlog.database.connection.get_database_path", return_value=db_path
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


def test_set_tracked(test_db: Path) -> None:
    """Test setting tracked flag for a nutrient."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Sodium", True)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT is_tracked FROM ref_daily_values WHERE nutrient_name = ?',
            ("Sodium",)
        )
        result = cursor.fetchone()[0]
        conn.close()

        assert result == 1


def test_set_tracked_to_false(test_db: Path) -> None:
    """Test unsetting tracked flag for a nutrient."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Sodium", True)
        repo.set_tracked("Sodium", False)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT is_tracked FROM ref_daily_values WHERE nutrient_name = ?',
            ("Sodium",)
        )
        result = cursor.fetchone()[0]
        conn.close()

        assert result == 0


def test_get_tracked_nutrients_empty(test_db: Path) -> None:
    """Test getting tracked nutrients when none are tracked."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        tracked = repo.get_tracked_nutrients()

        assert tracked == []


def test_get_tracked_nutrients_multiple(test_db: Path) -> None:
    """Test getting multiple tracked nutrients."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Sodium", True)
        repo.set_tracked("Calories", True)
        repo.set_tracked("Protein", True)

        tracked = repo.get_tracked_nutrients()

        assert "Sodium" in tracked
        assert "Calories" in tracked
        assert "Protein" in tracked
        assert len(tracked) == 3


def test_get_tracked_nutrients_returns_sorted(test_db: Path) -> None:
    """Test that tracked nutrients are returned in alphabetical order."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Zinc", True)
        repo.set_tracked("Calcium", True)
        repo.set_tracked("Sodium", True)

        tracked = repo.get_tracked_nutrients()

        assert tracked == ["Calcium", "Sodium", "Zinc"]


def test_list_all_nutrients(test_db: Path) -> None:
    """Test getting all nutrients."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        nutrients = repo.list_all_nutrients()

        assert len(nutrients) == 39
        assert all(isinstance(n, Nutrient) for n in nutrients)


def test_list_all_nutrients_sorted(test_db: Path) -> None:
    """Test that all nutrients are returned in alphabetical order."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        nutrients = repo.list_all_nutrients()
        names = [n.nutrient_name for n in nutrients]

        assert names == sorted(names)


def test_get_nutrient_by_id(test_db: Path) -> None:
    """Test getting a nutrient by ID."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()
        sodium = next(n for n in all_nutrients if n.nutrient_name == "Sodium")

        retrieved = repo.get_nutrient(sodium.nutrient_id)

        assert retrieved is not None
        assert retrieved.nutrient_name == "Sodium"
        assert retrieved.dv_amount == 2300000.0


def test_get_nutrient_by_id_not_found(test_db: Path) -> None:
    """Test getting a nutrient by nonexistent ID."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        result = repo.get_nutrient(99999)

        assert result is None


def test_get_by_name_found(test_db: Path) -> None:
    """Test getting a nutrient by name."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        nutrient = repo.get_by_name("Sodium")

        assert nutrient is not None
        assert nutrient.nutrient_name == "Sodium"
        assert nutrient.nutrient_fda_label_unit == "mg"
        assert nutrient.nutrient_entry_unit == "mg"
        assert nutrient.nutrient_dim_items_unit == "mcg"
        assert nutrient.dv_amount == 2300000.0


def test_get_by_name_vitamin_d(test_db: Path) -> None:
    """Test getting Vitamin D by name."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        nutrient = repo.get_by_name("Vitamin D")

        assert nutrient is not None
        assert nutrient.nutrient_name == "Vitamin D"
        assert nutrient.nutrient_fda_label_unit == "mcg"
        assert nutrient.nutrient_entry_unit == "%"
        assert nutrient.nutrient_dim_items_unit == "mcg"
        assert nutrient.dv_amount == 20.0


def test_get_by_name_not_found(test_db: Path) -> None:
    """Test getting a nutrient by nonexistent name."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        result = repo.get_by_name("Unknown Nutrient")

        assert result is None


def test_update_nutrient(test_db: Path) -> None:
    """Test updating nutrient name, dv_amount, and tracking flag."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()
        sodium = next(n for n in all_nutrients if n.nutrient_name == "Sodium")

        repo.update_nutrient(
            sodium.nutrient_id,
            "Sodium (Na)",
            2400000.0,
            1
        )

        updated = repo.get_nutrient(sodium.nutrient_id)

        assert updated.nutrient_name == "Sodium (Na)"
        assert updated.dv_amount == 2400000.0
        assert updated.is_tracked == 1


def test_update_nutrient_affects_get_by_name(test_db: Path) -> None:
    """Test that updating a nutrient's name affects get_by_name lookup."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()
        sodium = next(n for n in all_nutrients if n.nutrient_name == "Sodium")

        repo.update_nutrient(
            sodium.nutrient_id,
            "Sodium Modified",
            sodium.dv_amount,
            0
        )

        old_name_result = repo.get_by_name("Sodium")
        new_name_result = repo.get_by_name("Sodium Modified")

        assert old_name_result is None
        assert new_name_result is not None
        assert new_name_result.nutrient_name == "Sodium Modified"
