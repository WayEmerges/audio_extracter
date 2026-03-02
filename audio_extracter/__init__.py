"""Audio extracter - extract audio from video URLs and local files."""

from .config import OutputConfig
from .extractor import AudioExtractor
from .result import ExtractionResult
from .sources import FileVideoSource, LinkVideoSource, VideoSource

__all__ = [
    "AudioExtractor",
    "ExtractionResult",
    "FileVideoSource",
    "LinkVideoSource",
    "OutputConfig",
    "VideoSource",
]
