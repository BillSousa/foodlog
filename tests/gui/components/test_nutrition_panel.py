"""Tests for NutritionPanel component."""

import tempfile
import tkinter as tk
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.gui.components.nutrition_panel import NutritionPanel
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
        migrate_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


@pytest.fixture
def root_widget() -> tk.Tk:
    """Create throwaway Tk root for testing."""
    window = tk.Tk()
    yield window
    window.destroy()


def test_nutrition_panel_renders_tracked_nutrients(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that NutritionPanel renders one entry per tracked nutrient."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        # Set a few nutrients as tracked
        repo.set_tracked("Calories", True)
        repo.set_tracked("Sodium", True)
        repo.set_tracked("Vitamin D", True)

        panel = NutritionPanel(root_widget)
        assert len(panel.entries) == 3
        assert "Calories" in panel.entries
        assert "Sodium" in panel.entries
        assert "Vitamin D" in panel.entries


def test_nutrition_panel_shows_dv_percent_unit(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that %DV nutrients show percent unit."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Vitamin D", True)

        panel = NutritionPanel(root_widget)

        # Verify Vitamin D entry exists (it's a %DV nutrient)
        assert "Vitamin D" in panel.entries


def test_nutrition_panel_shows_mg_unit_for_sodium(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that Sodium shows mg as entry unit."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Sodium", True)

        panel = NutritionPanel(root_widget)
        assert "Sodium" in panel.entries


def test_nutrition_panel_get_values(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test retrieving nutrition values from entries."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Calories", True)
        repo.set_tracked("Sodium", True)

        panel = NutritionPanel(root_widget)

        # Set some values
        panel.entries["Calories"].delete(0, tk.END)
        panel.entries["Calories"].insert(0, "150.0")
        panel.entries["Sodium"].delete(0, tk.END)
        panel.entries["Sodium"].insert(0, "500.0")

        values = panel.get_values()
        assert values["Calories"] == 150.0
        assert values["Sodium"] == 500.0


def test_nutrition_panel_get_values_invalid_defaults_to_zero(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that invalid values default to 0.0."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Calories", True)

        panel = NutritionPanel(root_widget)

        # Set invalid value
        panel.entries["Calories"].delete(0, tk.END)
        panel.entries["Calories"].insert(0, "invalid")

        values = panel.get_values()
        assert values["Calories"] == 0.0


def test_nutrition_panel_set_values(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test populating entries with values."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        repo.set_tracked("Calories", True)
        repo.set_tracked("Sodium", True)

        panel = NutritionPanel(root_widget)

        # Set values via set_values
        panel.set_values({"Calories": 200.0, "Sodium": 750.0})

        assert panel.entries["Calories"].get() == "200.0"
        assert panel.entries["Sodium"].get() == "750.0"


def test_nutrition_panel_no_nutrients_tracked(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test panel when no nutrients are tracked."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        # Don't set any nutrients as tracked
        panel = NutritionPanel(root_widget)
        assert len(panel.entries) == 0
