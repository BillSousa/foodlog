from foodlog.models.dim_items import Item
from foodlog.repository.product_names_repository import ProductNamesRepository


def populate_item_form_data(
    item: Item,
    product_names_repo: ProductNamesRepository
) -> dict:
    """Extract item data for form population.

    Parameters
    ----------
    item : Item
        The item to extract data from.
    product_names_repo : ProductNamesRepository
        Used to resolve the item's product name.

    Returns
    -------
    dict
        Form field values keyed by field name:
        - name_text: str
        - price: str (stringified)
        - units: str
        - container_size: str (stringified)
        - serving_size: str (stringified)
        - active: bool
        - blocks_must_be_integer: bool
        - glycemic_index: str or None
        - nutrition_values: dict[str, float]
    """
    product_name = product_names_repo.get_product_name(item.name_id)

    nutrition_values = {
        k: v for k, v in item.to_dict().items()
        if k.endswith(("_g", "_mg", "_mcg"))
    }

    return {
        'name_text': product_name.name_text,
        'price': str(item.price),
        'units': item.units,
        'container_size': str(item.container_size),
        'serving_size': str(item.serving_size),
        'active': item.active == 1,
        'blocks_must_be_integer': item.blocks_must_be_integer == 1,
        'glycemic_index': (
            str(item.glycemic_index)
            if item.glycemic_index is not None
            else None
        ),
        'nutrition_values': nutrition_values,
    }
