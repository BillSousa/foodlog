from unittest.mock import MagicMock

from foodlog.gui.helpers.group_lines_by_category import (
    group_lines_by_category,
)
from foodlog.models.dim_categories import Category
from foodlog.models.dim_items import Item
from foodlog.models.fact_order_lines import OrderLine


def test_group_lines_by_category_single_category() -> None:
    """Group lines all in one category."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    line2 = OrderLine(
        line_id=2, order_id=1, item_id=20, actual_servings=2.0
    )
    lines = [line1, line2]

    item1 = Item(item_id=10, category_id=5)
    item2 = Item(item_id=20, category_id=5)

    items_repo = MagicMock()
    items_repo.get_item.side_effect = lambda id: (
        item1 if id == 10 else item2 if id == 20 else None
    )

    category = Category(category_id=5, category_name="Produce")
    categories_repo = MagicMock()
    categories_repo.get_category.return_value = category

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert len(result) == 1
    assert "Produce" in result
    assert len(result["Produce"]) == 2
    assert result["Produce"][0] == (line1, item1)
    assert result["Produce"][1] == (line2, item2)


def test_group_lines_by_category_multiple_categories() -> None:
    """Group lines across multiple categories."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    line2 = OrderLine(
        line_id=2, order_id=1, item_id=20, actual_servings=1.0
    )
    line3 = OrderLine(
        line_id=3, order_id=1, item_id=30, actual_servings=1.0
    )
    lines = [line1, line2, line3]

    item1 = Item(item_id=10, category_id=5)
    item2 = Item(item_id=20, category_id=6)
    item3 = Item(item_id=30, category_id=5)

    items_repo = MagicMock()
    items_repo.get_item.side_effect = lambda id: (
        item1 if id == 10 else item2 if id == 20 else item3 if id == 30
        else None
    )

    cat1 = Category(category_id=5, category_name="Produce")
    cat2 = Category(category_id=6, category_name="Meat")
    categories_repo = MagicMock()
    categories_repo.get_category.side_effect = lambda id: (
        cat1 if id == 5 else cat2 if id == 6 else None
    )

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert len(result) == 2
    assert "Produce" in result
    assert "Meat" in result
    assert len(result["Produce"]) == 2
    assert len(result["Meat"]) == 1
    assert result["Produce"][0] == (line1, item1)
    assert result["Produce"][1] == (line3, item3)
    assert result["Meat"][0] == (line2, item2)


def test_group_lines_by_category_uncategorized() -> None:
    """Items with no category go to (Uncategorized)."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    line2 = OrderLine(
        line_id=2, order_id=1, item_id=20, actual_servings=1.0
    )
    lines = [line1, line2]

    item1 = Item(item_id=10, category_id=None)
    item2 = Item(item_id=20, category_id=None)

    items_repo = MagicMock()
    items_repo.get_item.side_effect = lambda id: (
        item1 if id == 10 else item2 if id == 20 else None
    )

    categories_repo = MagicMock()

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert len(result) == 1
    assert "(Uncategorized)" in result
    assert len(result["(Uncategorized)"]) == 2
    assert result["(Uncategorized)"][0] == (line1, item1)
    assert result["(Uncategorized)"][1] == (line2, item2)


def test_group_lines_by_category_mixed() -> None:
    """Mix of categorized and uncategorized items."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    line2 = OrderLine(
        line_id=2, order_id=1, item_id=20, actual_servings=1.0
    )
    line3 = OrderLine(
        line_id=3, order_id=1, item_id=30, actual_servings=1.0
    )
    lines = [line1, line2, line3]

    item1 = Item(item_id=10, category_id=5)
    item2 = Item(item_id=20, category_id=None)
    item3 = Item(item_id=30, category_id=5)

    items_repo = MagicMock()
    items_repo.get_item.side_effect = lambda id: (
        item1 if id == 10 else item2 if id == 20 else item3 if id == 30
        else None
    )

    category = Category(category_id=5, category_name="Produce")
    categories_repo = MagicMock()
    categories_repo.get_category.return_value = category

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert len(result) == 2
    assert "Produce" in result
    assert "(Uncategorized)" in result
    assert len(result["Produce"]) == 2
    assert len(result["(Uncategorized)"]) == 1
    assert result["Produce"][0] == (line1, item1)
    assert result["Produce"][1] == (line3, item3)
    assert result["(Uncategorized)"][0] == (line2, item2)


def test_group_lines_by_category_order_preserved() -> None:
    """Lines in each category are in input order."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    line2 = OrderLine(
        line_id=2, order_id=1, item_id=20, actual_servings=1.0
    )
    line3 = OrderLine(
        line_id=3, order_id=1, item_id=30, actual_servings=1.0
    )
    line4 = OrderLine(
        line_id=4, order_id=1, item_id=40, actual_servings=1.0
    )
    lines = [line1, line2, line3, line4]

    item1 = Item(item_id=10, category_id=5)
    item2 = Item(item_id=20, category_id=6)
    item3 = Item(item_id=30, category_id=5)
    item4 = Item(item_id=40, category_id=6)

    items_repo = MagicMock()
    items_repo.get_item.side_effect = lambda id: (
        item1 if id == 10 else item2 if id == 20 else item3 if id == 30
        else item4 if id == 40 else None
    )

    cat1 = Category(category_id=5, category_name="Produce")
    cat2 = Category(category_id=6, category_name="Meat")
    categories_repo = MagicMock()
    categories_repo.get_category.side_effect = lambda id: (
        cat1 if id == 5 else cat2 if id == 6 else None
    )

    result = group_lines_by_category(lines, items_repo, categories_repo)

    # Both categories should have items in the order they appeared in input
    assert result["Produce"][0] == (line1, item1)
    assert result["Produce"][1] == (line3, item3)
    assert result["Meat"][0] == (line2, item2)
    assert result["Meat"][1] == (line4, item4)


def test_group_lines_by_category_missing_item() -> None:
    """Lines with missing items are skipped."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    line2 = OrderLine(
        line_id=2, order_id=1, item_id=20, actual_servings=1.0
    )
    line3 = OrderLine(
        line_id=3, order_id=1, item_id=30, actual_servings=1.0
    )
    lines = [line1, line2, line3]

    item1 = Item(item_id=10, category_id=5)
    item3 = Item(item_id=30, category_id=5)

    items_repo = MagicMock()
    items_repo.get_item.side_effect = lambda id: (
        item1 if id == 10 else item3 if id == 30 else None
    )

    category = Category(category_id=5, category_name="Produce")
    categories_repo = MagicMock()
    categories_repo.get_category.return_value = category

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert len(result) == 1
    assert len(result["Produce"]) == 2
    assert result["Produce"][0] == (line1, item1)
    assert result["Produce"][1] == (line3, item3)


def test_group_lines_by_category_missing_category() -> None:
    """Items with valid category_id but missing category fall to
    (Uncategorized)."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    lines = [line1]

    item1 = Item(item_id=10, category_id=99)

    items_repo = MagicMock()
    items_repo.get_item.return_value = item1

    categories_repo = MagicMock()
    categories_repo.get_category.return_value = None

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert len(result) == 1
    assert "(Uncategorized)" in result
    assert result["(Uncategorized)"][0] == (line1, item1)


def test_group_lines_by_category_empty_lines() -> None:
    """Empty lines list returns empty dict."""
    lines: list[OrderLine] = []
    items_repo = MagicMock()
    categories_repo = MagicMock()

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert result == {}


def test_group_lines_by_category_multiple_items_same_category() -> None:
    """Multiple items in same category are grouped together."""
    line1 = OrderLine(
        line_id=1, order_id=1, item_id=10, actual_servings=1.0
    )
    line2 = OrderLine(
        line_id=2, order_id=1, item_id=20, actual_servings=2.0
    )
    line3 = OrderLine(
        line_id=3, order_id=1, item_id=30, actual_servings=3.0
    )
    lines = [line1, line2, line3]

    item1 = Item(item_id=10, category_id=5)
    item2 = Item(item_id=20, category_id=5)
    item3 = Item(item_id=30, category_id=5)

    items_repo = MagicMock()
    items_repo.get_item.side_effect = lambda id: (
        item1 if id == 10 else item2 if id == 20 else item3 if id == 30
        else None
    )

    category = Category(category_id=5, category_name="Produce")
    categories_repo = MagicMock()
    categories_repo.get_category.return_value = category

    result = group_lines_by_category(lines, items_repo, categories_repo)

    assert len(result) == 1
    assert len(result["Produce"]) == 3
    assert result["Produce"][0] == (line1, item1)
    assert result["Produce"][1] == (line2, item2)
    assert result["Produce"][2] == (line3, item3)
