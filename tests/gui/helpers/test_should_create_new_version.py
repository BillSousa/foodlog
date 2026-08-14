import pytest

from foodlog.gui.helpers.should_create_new_version import (
    should_create_new_version,
)
from foodlog.models.dim_items import Item


def _make_complete_nutrition(
    units: str = 'oz',
    container_size: float = 250.0,
    serving_size: float = 40.0,
    **overrides: float
) -> dict[str, float]:
    """Build a complete nutrition dict with all columns defaulted to 0."""
    nutrition = {
        'units': units,
        'container_size': container_size,
        'serving_size': serving_size,
        'calories': 0.0,
        'total_fat_g': 0.0,
        'saturated_fat_g': 0.0,
        'trans_fat_g': 0.0,
        'cholesterol_mcg': 0.0,
        'sodium_mcg': 0.0,
        'total_carbs_g': 0.0,
        'dietary_fiber_g': 0.0,
        'total_sugars_g': 0.0,
        'added_sugars_g': 0.0,
        'protein_g': 0.0,
        'vitamin_d_mcg': 0.0,
        'calcium_mcg': 0.0,
        'iron_mcg': 0.0,
        'potassium_mcg': 0.0,
        'vitamin_a_mcg': 0.0,
        'vitamin_c_mcg': 0.0,
        'vitamin_e_mcg': 0.0,
        'vitamin_k_mcg': 0.0,
        'thiamin_mcg': 0.0,
        'riboflavin_mcg': 0.0,
        'niacin_mcg': 0.0,
        'vitamin_b6_mcg': 0.0,
        'folate_mcg': 0.0,
        'vitamin_b12_mcg': 0.0,
        'biotin_mcg': 0.0,
        'pantothenic_acid_mcg': 0.0,
        'phosphorus_mcg': 0.0,
        'iodine_mcg': 0.0,
        'magnesium_mcg': 0.0,
        'zinc_mcg': 0.0,
        'selenium_mcg': 0.0,
        'copper_mcg': 0.0,
        'manganese_mcg': 0.0,
        'chromium_mcg': 0.0,
        'molybdenum_mcg': 0.0,
        'chloride_mcg': 0.0,
        'choline_mcg': 0.0,
        'ethanol_g': 0.0,
    }
    nutrition.update(overrides)
    return nutrition


@pytest.fixture
def base_item() -> Item:
    """Create a base item for version testing."""
    return Item(
        item_id=1,
        name_id=1,
        category_id=2,
        price=5.0,
        servings_per_block=6.0,
        units="oz",
        container_size=250.0,
        serving_size=40.0,
        blocks_must_be_integer=1,
        active=1,
        glycemic_index=65,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
        choline_mcg=0.0,
    )


def test_should_create_new_version_no_changes(base_item: Item) -> None:
    """Return False when no nutrition fields change."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is False


def test_should_create_new_version_price_only_change(
    base_item: Item,
) -> None:
    """Return False when only price changes."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is False


def test_should_create_new_version_category_change(
    base_item: Item,
) -> None:
    """Return False when only category_id changes."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is False


def test_should_create_new_version_units_change(base_item: Item) -> None:
    """Return True when units change."""
    new_nutrition = _make_complete_nutrition(
        units='g',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_container_size_change(
    base_item: Item,
) -> None:
    """Return True when container_size changes."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=300.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_serving_size_change(
    base_item: Item,
) -> None:
    """Return True when serving_size changes."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=50.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_nutrient_change_fat(
    base_item: Item,
) -> None:
    """Return True when a nutrient column changes (total_fat_g)."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=10.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_nutrient_change_protein(
    base_item: Item,
) -> None:
    """Return True when a nutrient column changes (protein_g)."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=10.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_nutrient_to_zero(
    base_item: Item,
) -> None:
    """Return True when a nutrient changes to zero."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
        choline_mcg=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_multiple_changes(
    base_item: Item,
) -> None:
    """Return True when multiple nutrition fields change."""
    new_nutrition = _make_complete_nutrition(
        units='g',
        container_size=300.0,
        serving_size=50.0,
        total_fat_g=10.0,
        saturated_fat_g=3.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_none_to_value(
    base_item: Item,
) -> None:
    """Return True when a None nutrient becomes a value."""
    base_item.sodium_mcg = None
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_value_to_none(
    base_item: Item,
) -> None:
    """Return True when a nutrient value becomes None."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=None,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is True


def test_should_create_new_version_active_change(
    base_item: Item,
) -> None:
    """Return False when only active flag changes."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is False


def test_should_create_new_version_glycemic_index_change(
    base_item: Item,
) -> None:
    """Return False when only glycemic_index changes."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is False


def test_should_create_new_version_blocks_must_be_integer_change(
    base_item: Item,
) -> None:
    """Return False when only blocks_must_be_integer changes."""
    new_nutrition = _make_complete_nutrition(
        units='oz',
        container_size=250.0,
        serving_size=40.0,
        total_fat_g=8.0,
        saturated_fat_g=2.0,
        sodium_mcg=500000.0,
        total_carbs_g=20.0,
        protein_g=5.0,
    )
    assert should_create_new_version(base_item, new_nutrition) is False
