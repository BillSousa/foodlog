from foodlog.conversion.nutrition_converter import (
    get_nutrient_name,
    convert_nutrition_for_display,
)
from foodlog.models.dim_items import Item
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.product_names_repository import ProductNamesRepository


def populate_item_form_data(
    item: Item,
    product_names_repo: ProductNamesRepository,
    categories_repo: CategoriesRepository | None = None
) -> dict:
    """Extract item data for form population.

    Parameters
    ----------
    item : Item
        The item to extract data from.
    product_names_repo : ProductNamesRepository
        Used to resolve the item's product name.
    categories_repo : CategoriesRepository, optional
        Used to resolve the item's category name.

    Returns
    -------
    dict
        Form field values keyed by field name:
        - name_text: str
        - price: str (stringified)
        - units: str
        - container_size: str (stringified)
        - serving_size: str (stringified)
        - category_name: str or empty string
        - active: bool
        - blocks_must_be_integer: bool
        - glycemic_index: str or None
        - nutrition_values: dict[str, float]
    """
    product_name = product_names_repo.get_product_name(item.name_id)

    category_name = ''
    if item.category_id is not None:
        if categories_repo is None:
            categories_repo = CategoriesRepository()
        category = categories_repo.get_category(item.category_id)
        if category:
            category_name = category.category_name

    nutrition_values = {}
    for col_name, value in item.to_dict().items():
        nutrient_name = get_nutrient_name(col_name)
        if nutrient_name:
            display_value = convert_nutrition_for_display(
                nutrient_name, value
            )
            nutrition_values[nutrient_name] = display_value

    return {
        'name_text': product_name.name_text,
        'price': str(item.price),
        'units': item.units,
        'container_size': str(item.container_size),
        'serving_size': str(item.serving_size),
        'category_name': category_name,
        'active': item.active == 1,
        'blocks_must_be_integer': item.blocks_must_be_integer == 1,
        'glycemic_index': (
            str(item.glycemic_index)
            if item.glycemic_index is not None
            else None
        ),
        'nutrition_values': nutrition_values,
    }
