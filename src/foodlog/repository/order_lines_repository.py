from foodlog.database.connection import get_connection
from foodlog.models.fact_order_lines import OrderLine


class OrderLinesRepository:
    """CRUD for order line items."""

    def create_order_line(self, line: OrderLine) -> int:
        """Create order line item, return line_id."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO fact_order_lines
            (order_id, item_id, servings_ordered, actual_servings,
             stated_price, sale, discount, coupon, net_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                line.order_id,
                line.item_id,
                line.servings_ordered,
                line.actual_servings,
                line.stated_price,
                line.sale,
                line.discount,
                line.coupon,
                line.net_price,
            ),
        )
        conn.commit()
        line_id = cursor.lastrowid
        conn.close()
        return line_id

    def get_order_lines(self, order_id: int) -> list[OrderLine]:
        """Get all line items for an order."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM fact_order_lines WHERE order_id = ? ORDER BY line_id',
            (order_id,),
        )
        lines = [OrderLine(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return lines
