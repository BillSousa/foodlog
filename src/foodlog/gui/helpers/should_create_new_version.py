from foodlog.conversion.nutrition_converter import NUTRIENT_TO_COLUMN_MAP
from foodlog.models.dim_items import Item


def should_create_new_version(
    old_item: Item, new_nutrition: dict[str, float]
) -> bool:
    """Return True if any nutrition column differs from old_item.

    Parameters
    ----------
    old_item : Item
        The item as currently stored in the database.
    new_nutrition : dict[str, float]
        Column-name-keyed nutrition values from item_form_dialog,
        i.e. the output of running the form's raw nutrient values
        through `get_column_name()`/`convert_nutrition_for_storage()`.
        Should include all nutrition-affecting columns: the ~36 nutrient
        columns plus `units`, `container_size`, `serving_size`.

    Returns
    -------
    bool
        True if this is an SCD2-triggering change.
    """
    # Nutrition-affecting columns: all mapped nutrients plus serving/
    # container/units (which affect servings_per_block calculation)
    nutrition_affecting = set(NUTRIENT_TO_COLUMN_MAP.values())
    nutrition_affecting.update(['units', 'container_size', 'serving_size'])

    for column in nutrition_affecting:
        old_value = getattr(old_item, column, None)
        new_value = new_nutrition.get(column)
        if old_value != new_value:
            return True

    return False
