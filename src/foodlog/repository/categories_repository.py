from foodlog.database.connection import get_connection
from foodlog.models.dim_categories import Category


class CategoriesRepository:
    """CRUD for food categories."""

    def create_category(self, name: str) -> Category:
        """Create new category, return Category object."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO dim_categories (category_name) VALUES (?)',
            (name,)
        )
        conn.commit()
        cat_id = cursor.lastrowid
        conn.close()

        return Category(category_id=cat_id, category_name=name)

    def get_category(self, category_id: int) -> Category | None:
        """Get single category by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_categories WHERE category_id = ?',
                       (category_id,))
        row = cursor.fetchone()
        conn.close()
        return Category(**dict(row)) if row else None

    def list_categories(self) -> list[Category]:
        """Get all categories."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_categories ORDER BY category_name')
        categories = [Category(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return categories

    def update_category(self, category_id: int, name: str) -> None:
        """Update category name."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE dim_categories SET category_name = ? WHERE category_id = ?',
            (name, category_id)
        )
        conn.commit()
        conn.close()

    def delete_category(self, category_id: int) -> None:
        """Delete category by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM dim_categories WHERE category_id = ?',
                       (category_id,))
        conn.commit()
        conn.close()
