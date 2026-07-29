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

    def get_product_name(self, name_id: int) -> ProductName | None:
        """Get single product name by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_product_names WHERE name_id = ?',
                       (name_id,))
        row = cursor.fetchone()
        conn.close()
        return ProductName(**dict(row)) if row else None

    def list_product_names(self) -> list[ProductName]:
        """Get all product names."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_product_names ORDER BY name_text')
        names = [ProductName(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return names

    def update_product_name(self, name_id: int, name_text: str) -> None:
        """Update product name text."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE dim_product_names SET name_text = ? WHERE name_id = ?',
            (name_text, name_id)
        )
        conn.commit()
        conn.close()
