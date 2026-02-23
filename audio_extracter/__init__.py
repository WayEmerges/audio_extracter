"""Audio extracter - extract audio from video URLs and local files."""

from .config import OutputConfig
from .extractor import AudioExtractor
from .result import ExtractionResult
from .sources import LinkVideoSource, VideoSource

__all__ = [
    "AudioExtractor",
    "ExtractionResult",
    "LinkVideoSource",
    "OutputConfig",
    "VideoSource",
]
