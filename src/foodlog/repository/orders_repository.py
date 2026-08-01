from foodlog.database.connection import get_connection
from foodlog.models.fact_orders import Order


class OrdersRepository:
    """CRUD for orders with status transition validation."""

    def create_order(self, order: Order) -> int:
        """
        Create new order, return order_id.

        Returns:
            int: New order_id
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO fact_orders
            (order_date, is_delivery, status, delivery_charge, tip, tax,
             order_level_coupon, total_net_cost, total_calories,
             total_protein_g, total_carbs_g, total_fat_g, total_sodium_mg,
             ratio1, ratio2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (order.order_date, order.is_delivery, order.status,
             order.delivery_charge, order.tip, order.tax,
             order.order_level_coupon, order.total_net_cost,
             order.total_calories, order.total_protein_g, order.total_carbs_g,
             order.total_fat_g, order.total_sodium_mg, order.ratio1, order.ratio2)
        )
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        return order_id

    def get_order(self, order_id: int) -> Order | None:
        """Get order by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM fact_orders WHERE order_id = ?', (order_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Order(**dict(row))

    def list_orders(self) -> list[Order]:
        """Get all orders ordered by date DESC."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM fact_orders ORDER BY order_date DESC')
        orders = [Order(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return orders

    def update_order_status(self, order_id: int, new_status: str) -> None:
        """Update order status (planning/ordered/delivered/reconciled)."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE fact_orders SET status = ? WHERE order_id = ?',
            (new_status, order_id)
        )
        conn.commit()
        conn.close()

    def update_order_totals(self, order_id: int, **kwargs) -> None:
        """
        Update order-level totals/aggregates.

        Accepts: total_net_cost, total_calories, total_protein_g,
                 total_carbs_g, total_fat_g, total_sodium_mg, ratio1, ratio2
        """
        conn = get_connection()
        cursor = conn.cursor()

        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [order_id]

        cursor.execute(
            f'UPDATE fact_orders SET {set_clause} WHERE order_id = ?',
            values
        )
        conn.commit()
        conn.close()
