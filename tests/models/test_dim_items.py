from src.models.dim_items import Item


def test_item_default_values() -> None:
    """Test Item dataclass default values."""
    item = Item()
    assert item.item_id is None
    assert item.name_id == 0
    assert item.category_id is None
    assert item.price == 0.0
    assert item.active == 1
    assert item.calories == 0.0


def test_item_custom_values() -> None:
    """Test Item with custom values."""
    item = Item(
        item_id=1,
        name_id=5,
        category_id=2,
        price=2.99,
        active=0,
        calories=100.0,
        protein_g=10.0
    )
    assert item.item_id == 1
    assert item.name_id == 5
    assert item.category_id == 2
    assert item.price == 2.99
    assert item.active == 0
    assert item.calories == 100.0
    assert item.protein_g == 10.0


def test_item_to_dict() -> None:
    """Test to_dict() conversion."""
    item = Item(
        item_id=1,
        name_id=5,
        price=2.99,
        calories=100.0
    )
    d = item.to_dict()
    assert isinstance(d, dict)
    assert d['item_id'] == 1
    assert d['name_id'] == 5
    assert d['price'] == 2.99
    assert d['calories'] == 100.0
    assert 'protein_g' in d


def test_item_nutrition_columns_present() -> None:
    """Test all nutrition columns are in Item."""
    item = Item()
    nutrition_cols = [
        'calories', 'total_fat_g', 'saturated_fat_g', 'trans_fat_g',
        'cholesterol_mcg', 'sodium_mcg', 'total_carbs_g', 'dietary_fiber_g',
        'total_sugars_g', 'protein_g', 'vitamin_d_mcg', 'calcium_mcg',
        'iron_mcg', 'potassium_mcg'
    ]
    for col in nutrition_cols:
        assert hasattr(item, col)
        assert getattr(item, col) == 0.0
