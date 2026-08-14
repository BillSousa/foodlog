from unittest.mock import MagicMock

import pytest

from foodlog.gui.helpers.item_form_populator import (
    populate_item_form_data,
)
from foodlog.models.dim_items import Item
from foodlog.models.dim_product_names import ProductName


@pytest.fixture
def mock_product_names_repo() -> MagicMock:
    """Create a mock ProductNamesRepository."""
    return MagicMock()


@pytest.fixture
def test_item() -> Item:
    """Create a test item with full fields."""
    return Item(
        item_id=1,
        name_id=1,
        category_id=2,
        price=5.50,
        servings_per_block=6.25,
        units="oz",
        container_size=250.0,
        serving_size=40.0,
        blocks_must_be_integer=1,
        active=1,
        glycemic_index=65,
        calories=150.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
        choline_mcg=0.0,
    )


def test_populate_item_form_data_basic(
    test_item: Item, mock_product_names_repo: MagicMock
) -> None:
    """Test basic form data extraction."""
    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="White Bread"
    )

    result = populate_item_form_data(test_item, mock_product_names_repo)

    assert result["name_text"] == "White Bread"
    assert result["price"] == "5.5"
    assert result["units"] == "oz"
    assert result["container_size"] == "250.0"
    assert result["serving_size"] == "40.0"
    assert result["active"] is True
    assert result["blocks_must_be_integer"] is True
    assert result["glycemic_index"] == "65"


def test_populate_item_form_data_active_false(
    mock_product_names_repo: MagicMock,
) -> None:
    """Test active=0 converts to False."""
    item = Item(
        item_id=1,
        name_id=1,
        category_id=None,
        price=2.0,
        servings_per_block=1.0,
        units="g",
        container_size=100.0,
        serving_size=100.0,
        blocks_must_be_integer=0,
        active=0,
        glycemic_index=None,
        choline_mcg=0.0,
    )

    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test"
    )

    result = populate_item_form_data(item, mock_product_names_repo)

    assert result["active"] is False


def test_populate_item_form_data_blocks_must_be_integer_false(
    mock_product_names_repo: MagicMock,
) -> None:
    """Test blocks_must_be_integer=0 converts to False."""
    item = Item(
        item_id=1,
        name_id=1,
        category_id=None,
        price=2.0,
        servings_per_block=1.0,
        units="g",
        container_size=100.0,
        serving_size=100.0,
        blocks_must_be_integer=0,
        active=1,
        glycemic_index=None,
        choline_mcg=0.0,
    )

    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test"
    )

    result = populate_item_form_data(item, mock_product_names_repo)

    assert result["blocks_must_be_integer"] is False


def test_populate_item_form_data_glycemic_index_none(
    mock_product_names_repo: MagicMock,
) -> None:
    """Test glycemic_index=None stays None."""
    item = Item(
        item_id=1,
        name_id=1,
        category_id=None,
        price=2.0,
        servings_per_block=1.0,
        units="g",
        container_size=100.0,
        serving_size=100.0,
        blocks_must_be_integer=0,
        active=1,
        glycemic_index=None,
        choline_mcg=0.0,
    )

    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test"
    )

    result = populate_item_form_data(item, mock_product_names_repo)

    assert result["glycemic_index"] is None


def test_populate_item_form_data_nutrition_extraction(
    test_item: Item, mock_product_names_repo: MagicMock
) -> None:
    """Test nutrition values are extracted correctly."""
    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test Item"
    )

    result = populate_item_form_data(test_item, mock_product_names_repo)

    nutrition = result["nutrition_values"]
    assert nutrition["total_fat_g"] == 8.0
    assert nutrition["saturated_fat_g"] == 2.0
    assert nutrition["sodium_mcg"] == 500000.0
    assert nutrition["total_carbs_g"] == 20.0
    assert nutrition["protein_g"] == 5.0


def test_populate_item_form_data_nutrition_only_ends_with_suffix(
    mock_product_names_repo: MagicMock,
) -> None:
    """Test that only columns ending in _g, _mg, _mcg are extracted."""
    item = Item(
        item_id=1,
        name_id=1,
        category_id=None,
        price=2.0,
        servings_per_block=1.0,
        units="g",
        container_size=100.0,
        serving_size=100.0,
        blocks_must_be_integer=0,
        active=1,
        glycemic_index=None,
        calories=100.0,
        choline_mcg=0.0,
        protein_g=10.0,
    )

    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test"
    )

    result = populate_item_form_data(item, mock_product_names_repo)

    nutrition = result["nutrition_values"]
    assert "item_id" not in nutrition
    assert "name_id" not in nutrition
    assert "category_id" not in nutrition
    assert "price" not in nutrition
    assert "units" not in nutrition
    assert "container_size" not in nutrition
    assert "active" not in nutrition
    assert "glycemic_index" not in nutrition
    assert "calories" not in nutrition
    assert "protein_g" in nutrition


def test_populate_item_form_data_price_stringified(
    mock_product_names_repo: MagicMock,
) -> None:
    """Test that price is returned as a string."""
    item = Item(
        item_id=1,
        name_id=1,
        category_id=None,
        price=3.75,
        servings_per_block=1.0,
        units="g",
        container_size=100.0,
        serving_size=100.0,
        blocks_must_be_integer=0,
        active=1,
        glycemic_index=None,
        choline_mcg=0.0,
    )

    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test"
    )

    result = populate_item_form_data(item, mock_product_names_repo)

    assert isinstance(result["price"], str)
    assert result["price"] == "3.75"


def test_populate_item_form_data_sizes_stringified(
    mock_product_names_repo: MagicMock,
) -> None:
    """Test that container_size and serving_size are returned as strings."""
    item = Item(
        item_id=1,
        name_id=1,
        category_id=None,
        price=2.0,
        servings_per_block=2.5,
        units="oz",
        container_size=250.5,
        serving_size=100.2,
        blocks_must_be_integer=0,
        active=1,
        glycemic_index=None,
        choline_mcg=0.0,
    )

    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test"
    )

    result = populate_item_form_data(item, mock_product_names_repo)

    assert isinstance(result["container_size"], str)
    assert isinstance(result["serving_size"], str)
    assert result["container_size"] == "250.5"
    assert result["serving_size"] == "100.2"


def test_populate_item_form_data_resolves_product_name(
    test_item: Item, mock_product_names_repo: MagicMock
) -> None:
    """Test that product name is resolved via repository."""
    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Resolved Product Name"
    )

    populate_item_form_data(test_item, mock_product_names_repo)

    mock_product_names_repo.get_product_name.assert_called_once_with(
        test_item.name_id
    )


def test_populate_item_form_data_return_structure(
    test_item: Item, mock_product_names_repo: MagicMock
) -> None:
    """Test that return dict has all required keys."""
    mock_product_names_repo.get_product_name.return_value = ProductName(
        name_id=1, name_text="Test"
    )

    result = populate_item_form_data(test_item, mock_product_names_repo)

    required_keys = [
        "name_text",
        "price",
        "units",
        "container_size",
        "serving_size",
        "active",
        "blocks_must_be_integer",
        "glycemic_index",
        "nutrition_values",
    ]
    for key in required_keys:
        assert key in result
