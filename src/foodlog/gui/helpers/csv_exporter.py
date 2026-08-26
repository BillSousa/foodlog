import csv
from pathlib import Path


def export_rows_to_csv(
    path: Path, header: list[str], rows: list[list]
) -> None:
    """Write a header row and data rows to a CSV file.

    Parameters
    ----------
    path : Path
        Fully-resolved output file path (caller is responsible for
        the order-number + label + timestamp filename convention
        and for using `get_database_path().parent` as the directory,
        per SPEC §10 — this function just writes what it's given).
    header : list[str]
        Column headers, written as the first row.
    rows : list[list]
        Data rows, written in order after the header.
    """
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)
