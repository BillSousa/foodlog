from src.database.connection import get_connection


def is_first_run() -> bool:
    """
    Check if this is the first run (Setup Wizard not yet completed).

    Returns True if settings.wizard_completed is not set or is False.

    Returns:
        bool: True if first run, False if wizard already completed
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT setting_value FROM settings WHERE setting_key = ?',
        ('wizard_completed',)
    )
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return True

    value = result[0]
    return value == '0' or value == 'False' or value is None
