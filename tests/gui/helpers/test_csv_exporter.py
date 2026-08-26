import tempfile
from pathlib import Path

from foodlog.gui.helpers.csv_exporter import export_rows_to_csv


def test_export_rows_to_csv_basic() -> None:
    """Write header and data rows to CSV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        header = ["Name", "Price", "Quantity"]
        rows = [
            ["Chicken", "7.95", "1"],
            ["Potatoes", "4.49", "2"],
        ]

        export_rows_to_csv(csv_path, header, rows)

        assert csv_path.exists()
        content = csv_path.read_text()
        lines = content.strip().split('\n')
        assert lines[0] == "Name,Price,Quantity"
        assert lines[1] == "Chicken,7.95,1"
        assert lines[2] == "Potatoes,4.49,2"


def test_export_rows_to_csv_empty_rows() -> None:
    """Write header with no data rows."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        header = ["Column1", "Column2"]
        rows: list[list] = []

        export_rows_to_csv(csv_path, header, rows)

        assert csv_path.exists()
        content = csv_path.read_text()
        lines = content.strip().split('\n')
        assert len(lines) == 1
        assert lines[0] == "Column1,Column2"


def test_export_rows_to_csv_with_commas() -> None:
    """CSV escaping: commas in data are quoted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        header = ["Item", "Note"]
        rows = [
            ["Bread", "Store, Bakery"],
            ["Milk", "Regular"],
        ]

        export_rows_to_csv(csv_path, header, rows)

        content = csv_path.read_text()
        lines = content.strip().split('\n')
        # csv module should quote the field with a comma
        assert '"Store, Bakery"' in content or 'Store, Bakery' in lines[1]


def test_export_rows_to_csv_with_newlines() -> None:
    """CSV escaping: newlines in data are quoted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        header = ["Description"]
        rows = [
            ["Line 1\nLine 2"],
        ]

        export_rows_to_csv(csv_path, header, rows)

        assert csv_path.exists()
        content = csv_path.read_text()
        # csv module quotes fields with newlines
        assert '"Line 1' in content


def test_export_rows_to_csv_with_quotes() -> None:
    """CSV escaping: quotes in data are escaped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        header = ["Name"]
        rows = [
            ['John "Johnny" Doe'],
        ]

        export_rows_to_csv(csv_path, header, rows)

        content = csv_path.read_text()
        # csv module escapes quotes with double quotes
        assert '""' in content or '"John' in content


def test_export_rows_to_csv_numeric_data() -> None:
    """Write numeric data as strings to CSV."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        header = ["Item", "Price", "Quantity", "Total"]
        rows = [
            ["Chicken", "7.95", "1", "5.95"],
            ["Potatoes", "4.49", "2", "6.98"],
        ]

        export_rows_to_csv(csv_path, header, rows)

        content = csv_path.read_text()
        lines = content.strip().split('\n')
        assert "7.95" in lines[1]
        assert "6.98" in lines[2]


def test_export_rows_to_csv_file_overwrite() -> None:
    """Writing to existing file overwrites it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"

        # Write first version
        export_rows_to_csv(
            csv_path, ["A"], [["old_data"]]
        )
        assert "old_data" in csv_path.read_text()

        # Write second version (overwrite)
        export_rows_to_csv(
            csv_path, ["B", "C"], [["new", "data"]]
        )

        content = csv_path.read_text()
        assert "old_data" not in content
        assert "new" in content and "data" in content
