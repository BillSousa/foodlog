from foodlog.database.connection import get_connection
from foodlog.models.dim_items import Item


class ItemsRepository:
    """CRUD + SCD2 versioning for food items."""

    def create_item(self, item: Item) -> int:
        """
        Create new item, return item_id.

        Returns:
            int: New item_id
        """
        conn = get_connection()
        cursor = conn.cursor()

        columns = ', '.join(item.to_dict().keys())
        placeholders = ', '.join(['?'] * len(item.to_dict()))

        cursor.execute(
            f'INSERT INTO dim_items ({columns}) VALUES ({placeholders})',
            tuple(item.to_dict().values())
        )
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id

    def get_item(self, item_id: int) -> Item | None:
        """
        Get item by ID.

        Args:
            item_id: Item ID to retrieve

        Returns:
            Item or None if not found
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_items WHERE item_id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Item(**dict(row))

    def update_item_price(self, item_id: int, new_price: float) -> None:
        """
        Update price in place (SCD1 - overwrite).

        Args:
            item_id: Item to update
            new_price: New price per block
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE dim_items SET price = ? WHERE item_id = ?',
            (new_price, item_id)
        )
        conn.commit()
        conn.close()

    def create_item_version(self, template_item: Item) -> int:
        """
        Create new item version (SCD2) - for nutrition changes.

        Args:
            template_item: Item with updated nutrition, same name_id

        Returns:
            int: New item_id
        """
        conn = get_connection()
        cursor = conn.cursor()

        columns = ', '.join(template_item.to_dict().keys())
        placeholders = ', '.join(['?'] * len(template_item.to_dict()))

        cursor.execute(
            f'INSERT INTO dim_items ({columns}) VALUES ({placeholders})',
            tuple(template_item.to_dict().values())
        )
        conn.commit()
        new_item_id = cursor.lastrowid
        conn.close()
        return new_item_id

    def list_active_items(self) -> list[Item]:
        """
        Get all active items.

        Returns:
            list[Item]: All items with active=1
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dim_items WHERE active = 1 ORDER BY item_id')
        items = [Item(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return items

    def search_items(self, name_text: str) -> list[Item]:
        """
        Search items by name substring.

        Args:
            name_text: Substring to search for

        Returns:
            list[Item]: Matching active items
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT di.* FROM dim_items di
            JOIN dim_product_names dpn ON di.name_id = dpn.name_id
            WHERE di.active = 1 AND dpn.name_text LIKE ?
            ORDER BY dpn.name_text''',
            (f'%{name_text}%',)
        )
        items = [Item(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return items
