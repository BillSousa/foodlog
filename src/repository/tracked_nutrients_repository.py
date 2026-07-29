from src.database.connection import get_connection
from src.models.ref_daily_values import Nutrient


class TrackedNutrientsRepository:
    """Manage nutrient tracking flags in ref_daily_values."""

    def set_tracked(self, nutrient_name: str, is_tracked: bool) -> None:
        """Set is_tracked flag for a nutrient."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE ref_daily_values SET is_tracked = ? '
            'WHERE nutrient_name = ?',
            (1 if is_tracked else 0, nutrient_name)
        )
        conn.commit()
        conn.close()

    def get_tracked_nutrients(self) -> list[str]:
        """Get list of tracked nutrient names."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT nutrient_name FROM ref_daily_values '
            'WHERE is_tracked = 1 ORDER BY nutrient_name'
        )
        nutrients = [row[0] for row in cursor.fetchall()]
        conn.close()
        return nutrients

    def list_all_nutrients(self) -> list[Nutrient]:
        """Get all nutrients from ref_daily_values."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ref_daily_values ORDER BY nutrient_name')
        nutrients = [Nutrient(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return nutrients

    def get_nutrient(self, nutrient_id: int) -> Nutrient | None:
        """Get single nutrient by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ref_daily_values WHERE nutrient_id = ?',
                       (nutrient_id,))
        row = cursor.fetchone()
        conn.close()
        return Nutrient(**dict(row)) if row else None

    def update_nutrient(
        self, nutrient_id: int, name: str, dv_amount: float, is_tracked: int
    ) -> None:
        """Update nutrient name, daily value, and tracking flag."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE ref_daily_values SET nutrient_name = ?, '
            'dv_amount = ?, is_tracked = ? WHERE nutrient_id = ?',
            (name, dv_amount, is_tracked, nutrient_id)
        )
        conn.commit()
        conn.close()
