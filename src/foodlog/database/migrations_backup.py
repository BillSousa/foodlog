"""Idempotent schema migrations for existing databases."""

import sqlite3

from foodlog.database.seed_reference_data import NUTRIENTS


def migrate_schema(conn: sqlite3.Connection) -> None:
    """Apply idempotent schema migrations to an existing database.

    Safe to call on every startup, including against a database
    created fresh by `create_schema()` (which already has every
    column this function checks for).

    Parameters
    ----------
    conn : sqlite3.Connection
        Open database connection.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(ref_daily_values)")
    existing = {row[1] for row in cursor.fetchall()}
    for column in (
        "nutrient_fda_label_unit",
        "nutrient_entry_unit",
        "nutrient_dim_items_unit",
    ):
        if column not in existing:
            cursor.execute(
                f"ALTER TABLE ref_daily_values ADD COLUMN {column} "
                "TEXT NOT NULL DEFAULT ''"
            )

    for name, label_unit, entry_unit, dim_items_unit, _, _ in NUTRIENTS:
        cursor.execute(
            "UPDATE ref_daily_values SET nutrient_fda_label_unit = ?, "
            "nutrient_entry_unit = ?, nutrient_dim_items_unit = ? "
            "WHERE nutrient_name = ?",
            (label_unit, entry_unit, dim_items_unit, name),
        )
    conn.commit()
