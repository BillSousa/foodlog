from src.database.connection import get_connection
from src.models.dim_categories import Category


class CategoriesRepository:
    """CRUD for food categories."""

    def create_category(self, name: str) -> int:
        """Create new category, return category_id."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO dim_categories (category_name) VALUES (?)',
            (name,)
        )
        conn.commit()
        cat_id = cursor.lastrowid
        conn.close()
        return cat_id

    def list_categories(self) -> list[Category]:
        """Get all categories."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_categories ORDER BY category_name')
        categories = [Category(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return categories
