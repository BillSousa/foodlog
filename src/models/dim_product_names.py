from dataclasses import dataclass


@dataclass
class ProductName:
    """Product name dimension (SCD Type 0 - unchanging identity)."""

    name_id: int | None = None
    name_text: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'name_id': self.name_id,
            'name_text': self.name_text,
        }
