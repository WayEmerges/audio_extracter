"""Result type for audio extraction operations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExtractionResult:
    """Outcome of an audio extraction attempt."""

    success: bool
    output_path: Path | None = None
    metadata: dict[str, Any] | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        """Ensure output_path is a Path when present."""
        if self.output_path is not None and isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)
