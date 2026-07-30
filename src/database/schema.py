import sqlite3
from pathlib import Path


def create_schema(conn: sqlite3.Connection) -> None:
    """
    Create all FoodLog database tables if they don't exist.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_product_names (
            name_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_text TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ref_daily_values (
            nutrient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nutrient_name TEXT NOT NULL,
            dv_amount REAL NOT NULL,
            is_tracked INTEGER NOT NULL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_id INTEGER NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            servings_per_block REAL NOT NULL,
            units TEXT NOT NULL,
            container_size REAL NOT NULL,
            serving_size REAL NOT NULL,
            blocks_must_be_integer INTEGER NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            glycemic_index INTEGER,
            ratio1 REAL NOT NULL DEFAULT 0,
            ratio2 REAL NOT NULL DEFAULT 0,
            calories REAL NOT NULL DEFAULT 0,
            total_fat_g REAL NOT NULL DEFAULT 0,
            saturated_fat_g REAL NOT NULL DEFAULT 0,
            trans_fat_g REAL NOT NULL DEFAULT 0,
            cholesterol_mcg REAL NOT NULL DEFAULT 0,
            sodium_mcg REAL NOT NULL DEFAULT 0,
            total_carbs_g REAL NOT NULL DEFAULT 0,
            dietary_fiber_g REAL NOT NULL DEFAULT 0,
            total_sugars_g REAL NOT NULL DEFAULT 0,
            added_sugars_g REAL NOT NULL DEFAULT 0,
            protein_g REAL NOT NULL DEFAULT 0,
            vitamin_d_mcg REAL NOT NULL DEFAULT 0,
            calcium_mcg REAL NOT NULL DEFAULT 0,
            iron_mcg REAL NOT NULL DEFAULT 0,
            potassium_mcg REAL NOT NULL DEFAULT 0,
            vitamin_a_mcg REAL NOT NULL DEFAULT 0,
            vitamin_c_mcg REAL NOT NULL DEFAULT 0,
            vitamin_e_mcg REAL NOT NULL DEFAULT 0,
            vitamin_k_mcg REAL NOT NULL DEFAULT 0,
            thiamin_mcg REAL NOT NULL DEFAULT 0,
            riboflavin_mcg REAL NOT NULL DEFAULT 0,
            niacin_mcg REAL NOT NULL DEFAULT 0,
            vitamin_b6_mcg REAL NOT NULL DEFAULT 0,
            folate_mcg REAL NOT NULL DEFAULT 0,
            vitamin_b12_mcg REAL NOT NULL DEFAULT 0,
            biotin_mcg REAL NOT NULL DEFAULT 0,
            pantothenic_acid_mcg REAL NOT NULL DEFAULT 0,
            phosphorus_mcg REAL NOT NULL DEFAULT 0,
            iodine_mcg REAL NOT NULL DEFAULT 0,
            magnesium_mcg REAL NOT NULL DEFAULT 0,
            zinc_mcg REAL NOT NULL DEFAULT 0,
            selenium_mcg REAL NOT NULL DEFAULT 0,
            copper_mcg REAL NOT NULL DEFAULT 0,
            manganese_mcg REAL NOT NULL DEFAULT 0,
            chromium_mcg REAL NOT NULL DEFAULT 0,
            molybdenum_mcg REAL NOT NULL DEFAULT 0,
            chloride_mcg REAL NOT NULL DEFAULT 0,
            ethanol_g REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (name_id) REFERENCES dim_product_names(name_id),
            FOREIGN KEY (category_id) REFERENCES dim_categories(category_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT NOT NULL,
            is_delivery INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN
                ('planning', 'ordered', 'delivered', 'reconciled')),
            delivery_charge REAL NOT NULL DEFAULT 0,
            tip REAL NOT NULL DEFAULT 0,
            tax REAL NOT NULL DEFAULT 0,
            order_level_coupon REAL NOT NULL DEFAULT 0,
            total_net_cost REAL NOT NULL DEFAULT 0,
            total_calories REAL NOT NULL DEFAULT 0,
            total_protein_g REAL NOT NULL DEFAULT 0,
            total_carbs_g REAL NOT NULL DEFAULT 0,
            total_fat_g REAL NOT NULL DEFAULT 0,
            total_sodium_mg REAL NOT NULL DEFAULT 0,
            ratio1 REAL NOT NULL DEFAULT 0,
            ratio2 REAL NOT NULL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_order_lines (
            line_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            servings_ordered REAL NOT NULL,
            actual_servings REAL NOT NULL,
            stated_price REAL NOT NULL,
            sale REAL NOT NULL DEFAULT 0,
            discount REAL NOT NULL DEFAULT 0,
            coupon REAL NOT NULL DEFAULT 0,
            net_price REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES fact_orders(order_id),
            FOREIGN KEY (item_id) REFERENCES dim_items(item_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_consumption (
            consumption_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            servings_consumed REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES dim_items(item_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL
        )
    ''')

    conn.commit()
