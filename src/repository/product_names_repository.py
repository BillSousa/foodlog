from src.database.connection import get_connection
from src.models.dim_product_names import ProductName


class ProductNamesRepository:
    """CRUD for product names."""

    def create_product_name(self, name_text: str) -> int:
        """Create new product name, return name_id."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO dim_product_names (name_text) VALUES (?)',
            (name_text,)
        )
        conn.commit()
        name_id = cursor.lastrowid
        conn.close()
        return name_id

    def list_product_names(self) -> list[ProductName]:
        """Get all product names."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_product_names ORDER BY name_text')
        names = [ProductName(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return names
