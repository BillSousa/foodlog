from foodlog.database.connection import get_connection


def calculate_on_hand(item_id: int) -> float:
    """
    Calculate on-hand servings for an item.

    on_hand = SUM(fact_order_lines.actual_servings WHERE item_id)
              - SUM(fact_consumption.servings_consumed WHERE item_id)

    Args:
        item_id: Item ID

    Returns:
        float: Servings currently on hand (>=0, or negative if over-consumed)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT SUM(actual_servings) FROM fact_order_lines '
        'WHERE item_id = ?',
        (item_id,)
    )
    ordered_result = cursor.fetchone()
    ordered_servings = ordered_result[0] if ordered_result[0] else 0.0

    cursor.execute(
        'SELECT SUM(servings_consumed) FROM fact_consumption '
        'WHERE item_id = ?',
        (item_id,)
    )
    consumed_result = cursor.fetchone()
    consumed_servings = consumed_result[0] if consumed_result[0] else 0.0

    conn.close()

    return float(ordered_servings - consumed_servings)
