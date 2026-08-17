from foodlog.models.dim_items import Item
from foodlog.repository.product_names_repository import ProductNamesRepository


def filter_items(
    items: list[Item],
    search_text: str,
    selected_category_ids: list[int],
    product_names_repo: ProductNamesRepository,
) -> list[Item]:
    """Filter items by name match AND category membership.

    Parameters
    ----------
    items : list[Item]
        Candidate items (already resolved, e.g. list_active_items()).
    search_text : str
        Case-insensitive substring to match against the item's
        resolved product name. Empty string matches everything.
    selected_category_ids : list[int]
        Category IDs to restrict to. Empty list means no category
        filter (matches everything, regardless of category).
    product_names_repo : ProductNamesRepository
        Used to resolve each item's display name for the text match.

    Returns
    -------
    list[Item]
        Items matching the search text (if any) AND belonging to
        one of the selected categories (if any are selected). Both
        conditions apply simultaneously (AND), matching SPEC §10's
        "check Pasta then narrow further by typing" example.
    """
    result = []
    search_lower = search_text.lower()

    for item in items:
        if search_text:
            product_name = product_names_repo.get_product_name(
                item.name_id
            )
            name_text = product_name.name_text if product_name else ""
            if search_lower not in name_text.lower():
                continue

        if selected_category_ids:
            if item.category_id not in selected_category_ids:
                continue

        result.append(item)

    return result
