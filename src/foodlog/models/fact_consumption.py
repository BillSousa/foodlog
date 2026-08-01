from dataclasses import dataclass


@dataclass
class Consumption:
    """Consumption log entry - item consumed on a date."""

    consumption_id: int | None = None
    item_id: int = 0
    entry_date: str = ""
    servings_consumed: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {k: v for k, v in self.__dict__.items()}
