import tkinter as tk
from abc import ABC, abstractmethod


class BaseStep(ABC):
    """Base class for Setup Wizard steps."""

    def __init__(self, parent: tk.Widget) -> None:
        """
        Initialize step.

        Args:
            parent: Parent widget (wizard window)
        """
        self.parent = parent
        self.frame = tk.Frame(parent)

    @abstractmethod
    def layout(self) -> None:
        """Build step UI layout."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate step data before proceeding.

        Returns:
            bool: True if valid, False otherwise
        """
        pass

    @abstractmethod
    def save(self) -> None:
        """Save step data to database."""
        pass

    def get_frame(self) -> tk.Frame:
        """Return step's frame widget."""
        return self.frame

    def show(self) -> None:
        """Show this step's frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self) -> None:
        """Hide this step's frame."""
        self.frame.pack_forget()
