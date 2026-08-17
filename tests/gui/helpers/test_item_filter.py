import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.gui.helpers.item_filter import filter_items
from foodlog.models.dim_items import Item
from foodlog.repository.product_names_repository import ProductNamesRepository


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
def sample_items(test_db: Path) -> list[Item]:
    """Create sample items for testing."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        apple_id = names_repo.create_product_name("Apple")
        banana_id = names_repo.create_product_name("Banana")
        apple_pie_id = names_repo.create_product_name("Apple Pie")

        return [
            Item(
                item_id=1,
                name_id=apple_id,
                category_id=1,
                price=1.00,
                servings_per_block=2.0,
                units="oz",
                container_size=100,
                serving_size=10,
                blocks_must_be_integer=False,
                active=True,
                glycemic_index=None,
                calories=52.0,
                total_fat_g=0.2,
                sodium_mcg=100000.0,
                choline_mcg=3.6,
            ),
            Item(
                item_id=2,
                name_id=banana_id,
                category_id=2,
                price=0.50,
                servings_per_block=1.0,
                units="oz",
                container_size=100,
                serving_size=10,
                blocks_must_be_integer=False,
                active=True,
                glycemic_index=None,
                calories=89.0,
                total_fat_g=0.3,
                sodium_mcg=100000.0,
                choline_mcg=11.0,
            ),
            Item(
                item_id=3,
                name_id=apple_pie_id,
                category_id=1,
                price=5.00,
                servings_per_block=4.0,
                units="oz",
                container_size=100,
                serving_size=10,
                blocks_must_be_integer=False,
                active=True,
                glycemic_index=None,
                calories=237.0,
                total_fat_g=9.2,
                sodium_mcg=100000.0,
                choline_mcg=15.0,
            ),
        ]


def test_filter_items_no_filters(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test with no filters returns all items."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "", [], repo)
        assert len(result) == 3


def test_filter_items_by_search_text(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test search text filter."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "apple", [], repo)
        assert len(result) == 2
        assert sample_items[0] in result
        assert sample_items[2] in result
        assert sample_items[1] not in result


def test_filter_items_by_search_text_case_insensitive(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test search text is case-insensitive."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "APPLE", [], repo)
        assert len(result) == 2


def test_filter_items_by_category(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test category filter."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "", [1], repo)
        assert len(result) == 2
        assert sample_items[0] in result
        assert sample_items[2] in result
        assert sample_items[1] not in result


def test_filter_items_by_multiple_categories(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test filter with multiple categories."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "", [1, 2], repo)
        assert len(result) == 3


def test_filter_items_combined_search_and_category(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test combined search text and category filters."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "apple", [1], repo)
        assert len(result) == 2
        assert sample_items[0] in result
        assert sample_items[2] in result


def test_filter_items_combined_no_match(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test combined filters with no matches."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "apple", [2], repo)
        assert len(result) == 0


def test_filter_items_search_substring(
    test_db: Path, sample_items: list[Item]
) -> None:
    """Test search matches substring."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        repo = ProductNamesRepository()
        result = filter_items(sample_items, "ple", [], repo)
        assert len(result) == 2
        assert sample_items[0] in result
        assert sample_items[2] in result
