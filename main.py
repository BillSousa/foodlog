from src.database.connection import get_connection
from src.database.schema import create_schema
from src.database.seed_reference_data import seed_reference_data
from src.initialization.first_run_check import is_first_run
from src.initialization.initialize_defaults import initialize_defaults


def main() -> None:
    conn = get_connection()
    create_schema(conn)
    seed_reference_data(conn)
    conn.close()

    initialize_defaults()

    if is_first_run():
        from src.gui.windows.setup_wizard_window import launch_setup_wizard
        launch_setup_wizard()
    else:
        print("Welcome back! Opening main GUI (Phase 6).")


if __name__ == "__main__":
    main()
