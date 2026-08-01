from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.initialization.first_run_check import is_first_run
from foodlog.initialization.initialize_defaults import initialize_defaults


def main() -> None:
    conn = get_connection()
    create_schema(conn)
    seed_reference_data(conn)
    conn.close()

    initialize_defaults()

    if is_first_run():
        from foodlog.gui.windows.setup_wizard_window import launch_setup_wizard
        launch_setup_wizard()

    from foodlog.gui.windows.main_window import launch_main_gui
    launch_main_gui()


if __name__ == "__main__":
    main()
