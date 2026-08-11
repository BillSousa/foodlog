import sqlite3


# TODO: FOR VITAMINS AND MINERALS, nutrient_fda_label_unit IS IN mg/mcg AND 
# nutrient_entry_unit IS STILL IN %. ALTHOUGH EITHER MASS-ENTRY OR %-ENTRY CAN WORK, 
# MAY WANT TO REVISIT IN THE FUTURE AND DECIDE IF WE WANT nutrient_entry_unit IN mg/mcg.
NUTRIENTS = [
    ("Calories", "kcal", "kcal", "kcal", 2000, 0),
    ("Total Fat", "g", "g", "g", 78, 0),
    ("Saturated Fat", "g", "g", "g", 20, 0),
    ("Trans Fat", "g", "g", "g", 0, 0),
    ("Cholesterol", "mg", "mg", "mcg", 300000, 0),
    ("Sodium", "mg", "mg", "mcg", 2300000, 0),
    ("Total Carbohydrate", "g", "g", "g", 275, 0),
    ("Dietary Fiber", "g", "g", "g", 28, 0),
    ("Total Sugars", "g", "g", "g", 0, 0),
    ("Added Sugars", "g", "g", "g", 50, 0),
    ("Protein", "g", "g", "g", 50, 0),
    ("Vitamin D", "mcg", "%", "mcg", 20, 0),
    ("Calcium", "mg", "%", "mcg", 1300000, 0),
    ("Iron", "mg", "%", "mcg", 18000, 0),
    ("Potassium", "mg", "%", "mcg", 4700000, 0),
    ("Vitamin A", "mcg", "%", "mcg", 900, 0),
    ("Vitamin C", "mg", "%", "mcg", 90000, 0),
    ("Vitamin E", "mg", "%", "mcg", 15000, 0),
    ("Vitamin K", "mcg", "%", "mcg", 120, 0),
    ("Thiamin (Vitamin B1)", "mg", "%", "mcg", 1200, 0),
    ("Riboflavin (Vitamin B2)", "mg", "%", "mcg", 1300, 0),
    ("Niacin (Vitamin B3)", "mg", "%", "mcg", 16000, 0),
    ("Vitamin B6", "mg", "%", "mcg", 1700, 0),
    ("Folate", "mcg", "%", "mcg", 400, 0),
    ("Vitamin B12", "mcg", "%", "mcg", 2.4, 0),
    ("Biotin", "mcg", "%", "mcg", 30, 0),
    ("Pantothenic Acid", "mg", "%", "mcg", 5000, 0),
    ("Phosphorus", "mg", "%", "mcg", 1250000, 0),
    ("Iodine", "mcg", "%", "mcg", 150, 0),
    ("Magnesium", "mg", "%", "mcg", 420000, 0),
    ("Zinc", "mg", "%", "mcg", 11000, 0),
    ("Selenium", "mcg", "%", "mcg", 55, 0),
    ("Copper", "mg", "%", "mcg", 900, 0),
    ("Manganese", "mg", "%", "mcg", 2300, 0),
    ("Chromium", "mcg", "%", "mcg", 35, 0),
    ("Molybdenum", "mcg", "%", "mcg", 45, 0),
    ("Chloride", "mg", "%", "mcg", 2300000, 0),
    ("Choline", "mg", "%", "mcg", 550000, 0),
    ("Ethanol", "g", "g", "g", 0, 0),
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
        (nutrient_name, nutrient_fda_label_unit, nutrient_entry_unit,
         nutrient_dim_items_unit, dv_amount, is_tracked)
        VALUES (?, ?, ?, ?, ?, ?)''',
        [
            (name, label_unit, entry_unit, dim_items_unit, dv, tracked)
            for name, label_unit, entry_unit, dim_items_unit, dv, tracked
            in NUTRIENTS
        ]
    )

    conn.commit()
