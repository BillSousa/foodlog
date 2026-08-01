from foodlog.database.connection import get_connection
from foodlog.models.fact_consumption import Consumption


class ConsumptionRepository:
    """CRUD for consumption log entries."""

    def log_consumption(self, consumption: Consumption) -> int:
        """
        Log consumption entry, return consumption_id.

        Returns:
            int: New consumption_id
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO fact_consumption
            (item_id, entry_date, servings_consumed)
            VALUES (?, ?, ?)''',
            (consumption.item_id, consumption.entry_date,
             consumption.servings_consumed)
        )
        conn.commit()
        consumption_id = cursor.lastrowid
        conn.close()
        return consumption_id

    def get_consumption(self, consumption_id: int) -> Consumption | None:
        """Get consumption entry by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM fact_consumption WHERE consumption_id = ?',
            (consumption_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Consumption(**dict(row))

    def get_consumptions_for_item(self, item_id: int) -> list[Consumption]:
        """Get all consumption entries for an item."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM fact_consumption WHERE item_id = ? '
            'ORDER BY entry_date DESC',
            (item_id,)
        )
        consumptions = [Consumption(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return consumptions

    def total_consumed(self, item_id: int) -> float:
        """
        Get total servings consumed for an item.

        Args:
            item_id: Item ID

        Returns:
            float: Total servings consumed (0 if none)
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT SUM(servings_consumed) FROM fact_consumption '
            'WHERE item_id = ?',
            (item_id,)
        )
        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] is not None else 0.0
