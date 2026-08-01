from foodlog.database.connection import get_connection


def initialize_defaults() -> None:
    """
    Initialize default settings on fresh database.

    Sets:
    - cal_per_day_target = 2000 (daily calorie target)
    - wizard_completed = 0 (False, wizard not yet run)
    """
    conn = get_connection()
    cursor = conn.cursor()

    defaults = [
        ('cal_per_day_target', '2000'),
        ('wizard_completed', '0'),
    ]

    for key, value in defaults:
        cursor.execute(
            'INSERT OR IGNORE INTO settings (setting_key, setting_value) '
            'VALUES (?, ?)',
            (key, value)
        )

    conn.commit()
    conn.close()
