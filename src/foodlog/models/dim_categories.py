from dataclasses import dataclass


@dataclass
class Category:
    """Food category dimension."""

    category_id: int | None = None
    category_name: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
        }
