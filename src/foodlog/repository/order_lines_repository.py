from foodlog.database.connection import get_connection
from foodlog.models.fact_order_lines import OrderLine
from foodlog.validation.constraints import validate_order_editable


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

    def update_order_line(
        self,
        line_id: int,
        actual_servings: float | None = None,
        sale: float | None = None,
        discount: float | None = None,
        coupon: float | None = None,
        stated_price: float | None = None,
        net_price: float | None = None,
    ) -> None:
        """Update an existing order line's editable fields.

        Parameters
        ----------
        line_id : int
            Primary key of the line to update.
        actual_servings : float, optional
            New actual_servings value. If None, unchanged.
        sale : float, optional
            New sale value. If None, unchanged.
        discount : float, optional
            New discount value. If None, unchanged.
        coupon : float, optional
            New coupon value. If None, unchanged.
        stated_price : float, optional
            New stated_price value. If None, unchanged.
        net_price : float, optional
            New net_price value. If None, unchanged.

        Raises
        ------
        ValidationError
            If the parent order's status is reconciled (soft lock).

        Notes
        -----
        Never touches the frozen `servings_ordered` snapshot. This method
        updates only the fields that are provided (not None). All other
        fields remain unchanged. Callers must compute the new net_price
        if actual_servings, sale, discount, coupon, or stated_price change.
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT order_id FROM fact_order_lines WHERE line_id = ?',
            (line_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return

        order_id = row['order_id']

        cursor.execute(
            'SELECT status FROM fact_orders WHERE order_id = ?',
            (order_id,),
        )
        order_row = cursor.fetchone()
        conn.close()

        if order_row:
            order_status = order_row['status']
            validate_order_editable(order_status)

        fields_to_update = []
        values = []

        if actual_servings is not None:
            fields_to_update.append("actual_servings = ?")
            values.append(actual_servings)
        if sale is not None:
            fields_to_update.append("sale = ?")
            values.append(sale)
        if discount is not None:
            fields_to_update.append("discount = ?")
            values.append(discount)
        if coupon is not None:
            fields_to_update.append("coupon = ?")
            values.append(coupon)
        if stated_price is not None:
            fields_to_update.append("stated_price = ?")
            values.append(stated_price)
        if net_price is not None:
            fields_to_update.append("net_price = ?")
            values.append(net_price)

        if not fields_to_update:
            return

        values.append(line_id)
        set_clause = ", ".join(fields_to_update)
        query = f"UPDATE fact_order_lines SET {set_clause} WHERE line_id = ?"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()
