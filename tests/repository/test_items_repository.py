import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.database.connection import get_connection
from src.database.schema import create_schema
from src.database.seed_reference_data import seed_reference_data
from src.models.dim_items import Item
from src.models.dim_product_names import ProductName
from src.repository.items_repository import ItemsRepository


@pytest.fixture
def test_db() -> Path:
    """Create temp test database."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / 'test.db'
    with patch('src.database.connection.get_database_path', return_value=db_path):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


def test_create_item(test_db: Path) -> None:
    """Test creating a new item."""
    with patch('src.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            calories=100.0,
            protein_g=5.0
        )
        item_id = repo.create_item(item)
        assert item_id > 0


def test_get_item(test_db: Path) -> None:
    """Test retrieving an item."""
    with patch('src.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(
            name_id=1,
            price=2.99,
            servings_per_block=6.0,
            units='g',
            container_size=250,
            serving_size=40,
            calories=100.0
        )
        item_id = repo.create_item(item)
        retrieved = repo.get_item(item_id)
        assert retrieved is not None
        assert retrieved.item_id == item_id
        assert retrieved.price == 2.99
        assert retrieved.calories == 100.0


def test_update_item_price(test_db: Path) -> None:
    """Test updating item price (SCD1)."""
    with patch('src.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item = Item(name_id=1, price=2.99)
        item_id = repo.create_item(item)
        repo.update_item_price(item_id, 3.99)
        retrieved = repo.get_item(item_id)
        assert retrieved.price == 3.99


def test_list_active_items(test_db: Path) -> None:
    """Test listing active items."""
    with patch('src.database.connection.get_database_path', return_value=test_db):
        repo = ItemsRepository()
        item1 = Item(name_id=1, price=2.99, active=1)
        item2 = Item(name_id=2, price=3.99, active=1)
        repo.create_item(item1)
        repo.create_item(item2)
        items = repo.list_active_items()
        assert len(items) >= 2
        assert all(item.active == 1 for item in items)


def test_search_items(test_db: Path) -> None:
    """Test searching items by name."""
    with patch('src.database.connection.get_database_path', return_value=test_db):
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
        item = Item(name_id=name_id, price=2.99)
        repo.create_item(item)

        results = repo.search_items('Pasta')
        assert len(results) > 0
