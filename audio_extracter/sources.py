"""Video source abstractions for audio extraction."""

from abc import ABC, abstractmethod
from urllib.parse import urlparse


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
