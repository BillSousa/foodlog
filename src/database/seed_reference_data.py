import sqlite3


NUTRIENTS = [
    ("Calories", "kcal", 2000, 0, False),
    ("Total Fat", "g", 78, 0, False),
    ("Saturated Fat", "g", 20, 0, False),
    ("Trans Fat", "g", 0, 0, False),
    ("Cholesterol", "mcg", 300000, 0, False),
    ("Sodium", "mcg", 2300000, 0, False),
    ("Total Carbohydrate", "g", 275, 0, False),
    ("Dietary Fiber", "g", 28, 0, False),
    ("Total Sugars", "g", 50, 0, False),
    ("Added Sugars", "g", 50, 0, False),
    ("Protein", "g", 50, 0, False),
    ("Vitamin D", "mcg", 20, 0, True),
    ("Calcium", "mcg", 1300000, 0, True),
    ("Iron", "mcg", 18000, 0, True),
    ("Potassium", "mcg", 4700000, 0, True),
    ("Vitamin A", "mcg", 900, 0, True),
    ("Vitamin C", "mcg", 90000, 0, True),
    ("Vitamin E", "mcg", 15000, 0, True),
    ("Vitamin K", "mcg", 120, 0, True),
    ("Thiamin (Vitamin B1)", "mcg", 1200, 0, True),
    ("Riboflavin (Vitamin B2)", "mcg", 1300, 0, True),
    ("Niacin (Vitamin B3)", "mcg", 16000, 0, True),
    ("Vitamin B6", "mcg", 1700, 0, True),
    ("Folate", "mcg", 400, 0, True),
    ("Vitamin B12", "mcg", 2.4, 0, True),
    ("Biotin", "mcg", 30, 0, True),
    ("Pantothenic Acid", "mcg", 5000, 0, True),
    ("Phosphorus", "mcg", 1250000, 0, True),
    ("Iodine", "mcg", 150, 0, True),
    ("Magnesium", "mcg", 420000, 0, True),
    ("Zinc", "mcg", 11000, 0, True),
    ("Selenium", "mcg", 55, 0, True),
    ("Copper", "mcg", 900, 0, True),
    ("Manganese", "mcg", 2300, 0, True),
    ("Chromium", "mcg", 35, 0, True),
    ("Molybdenum", "mcg", 45, 0, True),
    ("Chloride", "mcg", 2300000, 0, False),
    ("Choline", "mcg", 550000, 0, True),
    ("Ethanol", "g", 0, 0, False),
]


def seed_reference_data(conn: sqlite3.Connection) -> None:
    """
    Populate ref_daily_values with FDA nutrient defaults.

    Only inserts if table is empty (idempotent).

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM ref_daily_values')
    if cursor.fetchone()[0] > 0:
        return

    cursor.executemany(
        '''INSERT INTO ref_daily_values
        (nutrient_name, dv_amount, is_tracked)
        VALUES (?, ?, ?)''',
        [(name, dv, tracked) for name, unit, dv, tracked, is_dv_percent in NUTRIENTS]
    )

    conn.commit()
