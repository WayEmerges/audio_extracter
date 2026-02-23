"""Configuration for audio extraction output."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OutputConfig:
    """Controls where and how extracted audio is saved."""

    format: str = "mp3"
    output_dir: Path = Path(".")
    filename_template: str = "%(title)s.%(ext)s"

    def __post_init__(self) -> None:
        """Ensure output_dir is a Path."""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
