from src.database.connection import get_connection


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
