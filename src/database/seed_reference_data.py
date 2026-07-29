import sqlite3


NUTRIENTS = [
    ("Calories", "kcal", 2000, 0),
    ("Total Fat", "g", 78, 0),
    ("Saturated Fat", "g", 20, 0),
    ("Trans Fat", "g", 0, 0),
    ("Cholesterol", "mcg", 300000, 0),
    ("Sodium", "mcg", 2300000, 0),
    ("Total Carbohydrate", "g", 275, 0),
    ("Dietary Fiber", "g", 28, 0),
    ("Total Sugars", "g", 50, 0),
    ("Added Sugars", "g", 50, 0),
    ("Protein", "g", 50, 0),
    ("Vitamin D", "mcg", 20, 0),
    ("Calcium", "mcg", 1300000, 0),
    ("Iron", "mcg", 18000, 0),
    ("Potassium", "mcg", 4700000, 0),
    ("Vitamin A", "mcg", 900, 0),
    ("Vitamin C", "mcg", 90000, 0),
    ("Vitamin E", "mcg", 15000, 0),
    ("Vitamin K", "mcg", 120, 0),
    ("Thiamin (Vitamin B1)", "mcg", 1200, 0),
    ("Riboflavin (Vitamin B2)", "mcg", 1300, 0),
    ("Niacin (Vitamin B3)", "mcg", 16000, 0),
    ("Vitamin B6", "mcg", 1700, 0),
    ("Folate", "mcg", 400, 0),
    ("Vitamin B12", "mcg", 2.4, 0),
    ("Biotin", "mcg", 30, 0),
    ("Pantothenic Acid", "mcg", 5000, 0),
    ("Phosphorus", "mcg", 1250000, 0),
    ("Iodine", "mcg", 150, 0),
    ("Magnesium", "mcg", 420000, 0),
    ("Zinc", "mcg", 11000, 0),
    ("Selenium", "mcg", 55, 0),
    ("Copper", "mcg", 900, 0),
    ("Manganese", "mcg", 2300, 0),
    ("Chromium", "mcg", 35, 0),
    ("Molybdenum", "mcg", 45, 0),
    ("Chloride", "mcg", 2300000, 0),
    ("Choline", "mcg", 550000, 0),
    ("Ethanol", "g", 0, 0),
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
        [(name, dv, tracked) for name, unit, dv, tracked in NUTRIENTS]
    )

    conn.commit()
