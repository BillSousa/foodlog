from src.database.connection import get_connection
from src.database.schema import create_schema
from src.database.seed_reference_data import seed_reference_data


def main() -> None:
    conn = get_connection()
    create_schema(conn)
    seed_reference_data(conn)
    print("FoodLog database initialized. ✓")
    conn.close()


if __name__ == "__main__":
    main()
