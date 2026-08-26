from foodlog.models.dim_items import Item
from foodlog.models.fact_order_lines import OrderLine
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.items_repository import ItemsRepository


def group_lines_by_category(
    lines: list[OrderLine],
    items_repo: ItemsRepository,
    categories_repo: CategoriesRepository,
) -> dict[str, list[tuple[OrderLine, Item]]]:
    """Group order lines by their item's category display name.

    Parameters
    ----------
    lines : list[OrderLine]
        All lines belonging to one order.
    items_repo : ItemsRepository
        Used to resolve each line's Item (for category_id and
        nutrition/price data the caller will need downstream).
    categories_repo : CategoriesRepository
        Used to resolve category_id to a display name.

    Returns
    -------
    dict[str, list[tuple[OrderLine, Item]]]
        Keys are category display names, or the literal string
        "(Uncategorized)" for items with category_id=None (this
        string is for display only and is never written to
        dim_categories). Each value is a list of (line, item) pairs
        in that category, in the same relative order as the input.
        This function only groups — computing subtotals/totals from
        each group's values is the caller's responsibility, since
        the two summary windows subtotal different things (money vs.
        nutrient columns).
    """
    result: dict[str, list[tuple[OrderLine, Item]]] = {}

    for line in lines:
        item = items_repo.get_item(line.item_id)
        if not item:
            continue

        if item.category_id is None:
            category_key = "(Uncategorized)"
        else:
            category = categories_repo.get_category(item.category_id)
            if category:
                category_key = category.category_name
            else:
                category_key = "(Uncategorized)"

        if category_key not in result:
            result[category_key] = []
        result[category_key].append((line, item))

    return result
