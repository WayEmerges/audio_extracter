"""Video source abstractions for audio extraction."""

from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlparse


# Common video extensions (no image formats like PNG – those have no audio to extract)
VIDEO_EXTENSIONS = frozenset(
    {
        ".mp4", ".m4v", ".webm", ".mkv", ".avi", ".mov", ".flv", ".wmv",
        ".ogv", ".3gp", ".mpeg", ".mpg", ".ts", ".m2ts",
    }
)


class VideoSource(ABC):
    """Abstract base for any video input (URL, file path, etc.)."""

    @abstractmethod
    def get_source_identifier(self) -> str:
        """Return a unique identifier for this source (e.g., URL or file path)."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate that this source is usable. Returns True if valid."""
        pass


class LinkVideoSource(VideoSource):
    """Represents a video accessible via URL (YouTube, Vimeo, etc.)."""

    def __init__(self, url: str) -> None:
        self._url = url.strip()
        self._parsed = urlparse(self._url)

    def get_source_identifier(self) -> str:
        return self._url

    def validate(self) -> bool:
        """Check URL format: must have scheme (http/https) and netloc (domain)."""
        if not self._url:
            return False
        return self._parsed.scheme in ("http", "https") and bool(self._parsed.netloc)


class FileVideoSource(VideoSource):
    """Represents a local video file (e.g. .mp4, .webm, .mkv) for audio extraction."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path).resolve() if path else None

    def get_source_identifier(self) -> str:
        return str(self._path) if self._path else ""

    def validate(self) -> bool:
        """Check file exists and has a known video extension."""
        if not self._path:
            return False
        if not self._path.is_file():
            return False
        return self._path.suffix.lower() in VIDEO_EXTENSIONS
