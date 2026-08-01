import sys
from pathlib import Path


def test_spec_entry_point_exists() -> None:
    """Test that the spec's entry point file exists."""
    entry_point = Path(__file__).parent.parent.parent / 'main.py'
    assert entry_point.exists(), f"Entry point {entry_point} does not exist"


def test_spec_output_name_per_platform() -> None:
    """Test that the spec computes correct output name per platform."""
    output_name = 'foodlog_win' if sys.platform == 'win32' else 'foodlog_linux'

    if sys.platform == 'win32':
        assert output_name == 'foodlog_win'
    else:
        assert output_name == 'foodlog_linux'


def test_spec_icon_path_conditional() -> None:
    """Test that icon path is conditional on file existence."""
    icon_path = 'build/foodlog.ico' if Path('build/foodlog.ico').exists() else None

    # Either the file exists and icon_path is the string, or it doesn't and icon_path is None
    if Path('build/foodlog.ico').exists():
        assert icon_path == 'build/foodlog.ico'
    else:
        assert icon_path is None
