from foodlog.database.connection import get_connection


class SettingsRepository:
    """CRUD for application settings."""

    def get_setting(self, key: str) -> str | None:
        """Get setting value by key."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT setting_value FROM settings WHERE setting_key = ?',
            (key,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_setting(self, key: str, value: str) -> None:
        """Set or update setting."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO settings '
            '(setting_key, setting_value) VALUES (?, ?)',
            (key, value)
        )
        conn.commit()
        conn.close()
