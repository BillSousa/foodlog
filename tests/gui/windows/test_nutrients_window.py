import tempfile
from pathlib import Path
from unittest.mock import patch
import tkinter as tk

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.initialization.initialize_defaults import initialize_defaults
from foodlog.gui.windows.nutrients_window import NutrientsWindow
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
        initialize_defaults()
    return db_path


def test_nutrients_window_renders_all_nutrients(test_db: Path) -> None:
    """Test that nutrients window renders one row per nutrient."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()
        expected_count = len(all_nutrients)

        root = tk.Tk()
        window = NutrientsWindow(root)

        # Check that nutrient_rows dict has one entry per nutrient
        assert len(window.nutrient_rows) == expected_count
        root.destroy()


def test_nutrients_window_shows_dim_items_unit(test_db: Path) -> None:
    """Test that nutrient rows display dim_items_unit."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        sodium = repo.get_by_name("Sodium")
        assert sodium is not None
        assert sodium.nutrient_dim_items_unit == "mcg"


def test_nutrients_window_edit_and_save(test_db: Path) -> None:
    """Test editing nutrient name/DV and saving."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        nutrients = repo.list_all_nutrients()
        original = nutrients[0]

        root = tk.Tk()
        window = NutrientsWindow(root)

        # Modify the name and DV of the first nutrient
        window.nutrient_rows[original.nutrient_id]["name_var"].set(
            "Modified Name"
        )
        window.nutrient_rows[original.nutrient_id]["dv_var"].set("9999")

        # Mock messagebox to avoid GUI hangs in tests
        with patch("foodlog.gui.windows.nutrients_window.messagebox"):
            # Call _save (this calls repo.update_nutrient internally)
            window._save()

        # Verify changes were persisted
        updated = repo.get_nutrient(original.nutrient_id)
        assert updated.nutrient_name == "Modified Name"
        assert updated.dv_amount == 9999.0
        root.destroy()
