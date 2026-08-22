"""Pytest configuration for GUI tests."""
import tkinter as tk
import pytest


@pytest.fixture(autouse=True)
def cleanup_tk_windows():
    """Auto-cleanup all Tk Toplevel windows after each test."""
    yield
    # After test, destroy all remaining Toplevel windows
    # We collect them first to avoid modifying the list while iterating
    toplevels = [w for w in tk.Tk().winfo_toplevel().winfo_children()
                 if isinstance(w, tk.Toplevel)]
    for window in toplevels:
        try:
            if window.winfo_exists():
                window.destroy()
        except tk.TclError:
            # Window already destroyed, skip
            pass
