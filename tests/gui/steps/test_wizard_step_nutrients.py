"""Tests for NutrientsStep in setup wizard."""

import tempfile
import tkinter as tk
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.gui.steps.wizard_step_nutrients import NutrientsStep
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


def test_nutrients_step_creates_checkbox_for_each_nutrient(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that NutrientsStep creates a checkbox for every nutrient."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        step = NutrientsStep(root_widget)
        step.layout()

        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()

        assert len(step.check_vars) == len(all_nutrients)
        for nutrient in all_nutrients:
            assert nutrient.nutrient_name in step.check_vars


def test_nutrients_step_identifies_vitamin_mineral_nutrients(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that %DV nutrients are correctly identified."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        step = NutrientsStep(root_widget)
        step.layout()

        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()
        dv_percent_nutrients = [
            n for n in all_nutrients
            if n.nutrient_entry_unit == "%"
        ]

        assert len(step.vitamin_vars) == len(dv_percent_nutrients)
        assert len(step.vitamin_vars) == 27


def test_master_toggle_controls_all_vitamin_mineral_nutrients(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that master toggle affects all 27 vitamin/mineral rows."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        step = NutrientsStep(root_widget)
        step.layout()

        # Turn on master toggle
        step.master_var.set(True)

        # All vitamin_vars should be True
        for var in step.vitamin_vars:
            assert var.get() is True

        # Turn off master toggle
        step.master_var.set(False)

        # All vitamin_vars should be False
        for var in step.vitamin_vars:
            assert var.get() is False


def test_master_toggle_does_not_affect_non_vitamin_nutrients(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that master toggle leaves non-vitamin rows unchanged."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        step = NutrientsStep(root_widget)
        step.layout()

        repo = TrackedNutrientsRepository()
        all_nutrients = repo.list_all_nutrients()
        non_dv_nutrients = [
            n for n in all_nutrients
            if n.nutrient_entry_unit != "%"
        ]

        # Manually set some non-DV nutrients to True
        non_dv_vars = [
            step.check_vars[n.nutrient_name]
            for n in non_dv_nutrients[:3]
        ]
        for var in non_dv_vars:
            var.set(True)

        # Toggle master (affects only DV nutrients)
        step.master_var.set(True)

        # Non-DV nutrients should still be True (unchanged)
        for var in non_dv_vars:
            assert var.get() is True


def test_nutrients_step_validate_always_true(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that validate returns True (step is always valid)."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        step = NutrientsStep(root_widget)
        assert step.validate() is True


def test_nutrients_step_save_persists_checked_nutrients(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that save() persists only checked nutrients."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        step = NutrientsStep(root_widget)
        step.layout()

        # Check only Calories and Sodium
        step.check_vars["Calories"].set(True)
        step.check_vars["Sodium"].set(True)

        step.save()

        # Verify they're persisted as tracked
        repo = TrackedNutrientsRepository()
        tracked = set(repo.get_tracked_nutrients())
        assert "Calories" in tracked
        assert "Sodium" in tracked

        # Verify others are not tracked
        assert "Vitamin D" not in tracked


def test_nutrients_step_save_with_no_nutrients_checked(
    test_db: Path, root_widget: tk.Tk
) -> None:
    """Test that save() works when no nutrients are checked."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        step = NutrientsStep(root_widget)
        step.layout()

        # Don't check anything
        step.save()

        # Verify nothing is tracked
        repo = TrackedNutrientsRepository()
        tracked = set(repo.get_tracked_nutrients())
        assert len(tracked) == 0
