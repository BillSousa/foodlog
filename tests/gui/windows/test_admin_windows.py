import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.initialization.initialize_defaults import initialize_defaults
from foodlog.repository.settings_repository import SettingsRepository
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.product_names_repository import ProductNamesRepository
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


def test_settings_get_cal_target(test_db: Path) -> None:
    """Test getting calorie target from settings."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = SettingsRepository()
        val = repo.get_setting("cal_per_day_target")
        assert val == "2000"


def test_settings_set_cal_target(test_db: Path) -> None:
    """Test setting calorie target."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = SettingsRepository()
        repo.set_setting("cal_per_day_target", "2500")
        val = repo.get_setting("cal_per_day_target")
        assert val == "2500"


def test_categories_create(test_db: Path) -> None:
    """Test creating a category."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = CategoriesRepository()
        cat = repo.create_category("Produce")
        assert cat is not None
        assert cat.category_name == "Produce"


def test_categories_update(test_db: Path) -> None:
    """Test updating a category name."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = CategoriesRepository()
        cat = repo.create_category("Produce")
        cat_id = cat.category_id

        repo.update_category(cat_id, "Vegetables")
        updated = repo.get_category(cat_id)
        assert updated.category_name == "Vegetables"


def test_categories_delete(test_db: Path) -> None:
    """Test deleting a category."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = CategoriesRepository()
        cat = repo.create_category("Produce")
        cat_id = cat.category_id

        repo.delete_category(cat_id)
        deleted = repo.get_category(cat_id)
        assert deleted is None


def test_product_names_update(test_db: Path) -> None:
    """Test updating a product name."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        names = repo.list_product_names()
        if names:
            name_id = names[0].name_id
            repo.update_product_name(name_id, "Updated Name")
            updated = repo.get_product_name(name_id)
            assert updated.name_text == "Updated Name"


def test_nutrients_update(test_db: Path) -> None:
    """Test updating nutrient tracking."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = TrackedNutrientsRepository()
        nutrients = repo.list_all_nutrients()
        if nutrients:
            nutrient_id = nutrients[0].nutrient_id
            repo.update_nutrient(nutrient_id, "Test Nutrient", 5000, 1)

            updated = repo.get_nutrient(nutrient_id)
            assert updated.nutrient_name == "Test Nutrient"
            assert updated.dv_amount == 5000
            assert updated.is_tracked == 1
