import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.dim_items import Item
from foodlog.models.dim_product_names import ProductName
from foodlog.repository.items_repository import ItemsRepository


@pytest.fixture
def test_db() -> Path:
    """Create temp test database."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / 'test.db'
    with patch('foodlog.database.connection.get_database_path', return_value=db_path):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


def test_create_item(test_db: Path) -> None:
    """Test creating a new item."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            calories=100.0,
            protein_g=5.0,
            choline_mcg=0,
        )
        item_id = repo.create_item(item)
        assert item_id > 0


def test_get_item(test_db: Path) -> None:
    """Test retrieving an item."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            calories=100.0,
            choline_mcg=0,
        )
        item_id = repo.create_item(item)
        retrieved = repo.get_item(item_id)
        assert retrieved is not None
        assert retrieved.item_id == item_id
        assert retrieved.price == 2.99
        assert retrieved.calories == 100.0


def test_update_item_price(test_db: Path) -> None:
    """Test updating item price (SCD1)."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(name_id=1, price=2.99, units='g', choline_mcg=0)
        item_id = repo.create_item(item)
        repo.update_item_price(item_id, 3.99)
        retrieved = repo.get_item(item_id)
        assert retrieved.price == 3.99


def test_list_active_items(test_db: Path) -> None:
    """Test listing active items."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item1 = Item(name_id=1, price=2.99, active=1, units='g', choline_mcg=0)
        item2 = Item(name_id=2, price=3.99, active=1, units='g', choline_mcg=0)
        repo.create_item(item1)
        repo.create_item(item2)
        items = repo.list_active_items()
        assert len(items) >= 2
        assert all(item.active == 1 for item in items)


def test_search_items(test_db: Path) -> None:
    """Test searching items by name."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        # Insert product name first
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO dim_product_names (name_text) VALUES (?)',
            ('Pasta Spaghetti',)
        )
        conn.commit()
        name_id = cursor.lastrowid
        conn.close()

        repo = ItemsRepository()
        item = Item(name_id=name_id, price=2.99, units='g', choline_mcg=0)
        repo.create_item(item)

        results = repo.search_items('Pasta')
        assert len(results) > 0


def test_create_item_version_returns_new_id(test_db: Path) -> None:
    """Test that create_item_version returns a new item_id."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=5.0,
            choline_mcg=0,
        )
        old_item_id = repo.create_item(item)

        new_item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=10.0,
            choline_mcg=0,
        )
        new_item_id = repo.create_item_version(new_item)

        assert new_item_id != old_item_id
        assert new_item_id > 0


def test_create_item_version_preserves_old_item(
    test_db: Path,
) -> None:
    """Test that old item_id remains valid after versioning."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=5.0,
            choline_mcg=0,
        )
        old_item_id = repo.create_item(item)
        old_item = repo.get_item(old_item_id)

        new_item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=10.0,
            choline_mcg=0,
        )
        repo.create_item_version(new_item)

        retrieved_old = repo.get_item(old_item_id)
        assert retrieved_old is not None
        assert retrieved_old.item_id == old_item_id
        assert retrieved_old.protein_g == old_item.protein_g


def test_create_item_version_same_name_id(test_db: Path) -> None:
    """Test that old and new versions share the same name_id."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=5.0,
            choline_mcg=0,
        )
        old_item_id = repo.create_item(item)
        old_item = repo.get_item(old_item_id)

        new_item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=10.0,
            choline_mcg=0,
        )
        new_item_id = repo.create_item_version(new_item)
        new_item_retrieved = repo.get_item(new_item_id)

        assert old_item.name_id == new_item_retrieved.name_id


def test_create_item_version_nutrition_differs(test_db: Path) -> None:
    """Test that nutrition values differ between versions."""
    with patch('foodlog.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=5.0,
            sodium_mcg=100000.0,
            choline_mcg=0,
        )
        old_item_id = repo.create_item(item)

        new_item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            protein_g=10.0,
            sodium_mcg=200000.0,
            choline_mcg=0,
        )
        new_item_id = repo.create_item_version(new_item)

        old_retrieved = repo.get_item(old_item_id)
        new_retrieved = repo.get_item(new_item_id)

        assert old_retrieved.protein_g != new_retrieved.protein_g
        assert old_retrieved.sodium_mcg != new_retrieved.sodium_mcg
