"""Audio extraction from video sources."""

import subprocess
from pathlib import Path

import yt_dlp

from .config import OutputConfig
from .result import ExtractionResult
from .sources import FileVideoSource, LinkVideoSource, VideoSource


class AudioExtractor:
    """Extracts audio from video sources using yt-dlp and ffmpeg."""

    def extract(self, source: VideoSource, config: OutputConfig) -> ExtractionResult:
        """Extract audio from the given source. Returns ExtractionResult."""
        if not source.validate():
            return ExtractionResult(
                success=False,
                error_message="Invalid video source",
            )

        if isinstance(source, LinkVideoSource):
            return self._extract_from_link(source, config)
        if isinstance(source, FileVideoSource):
            return self._extract_from_file(source, config)

        return ExtractionResult(
            success=False,
            error_message=f"Unsupported source type: {type(source).__name__}",
        )

    def _extract_from_link(
        self, source: LinkVideoSource, config: OutputConfig
    ) -> ExtractionResult:
        """Extract audio from a URL using yt-dlp."""
        config.output_dir.mkdir(parents=True, exist_ok=True)

        outtmpl = str(config.output_dir / config.filename_template)

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": config.format,
                }
            ],
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source.get_source_identifier(), download=True)
                if info is None:
                    return ExtractionResult(
                        success=False,
                        error_message="Could not extract video info",
                    )

                output_path = self._get_output_path(info, config)
                metadata = {
                    "title": info.get("title", ""),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader"),
                }

                return ExtractionResult(
                    success=True,
                    output_path=output_path,
                    metadata=metadata,
                )

        except yt_dlp.utils.DownloadError as e:
            return ExtractionResult(
                success=False,
                error_message=str(e).split("\n")[0],
            )
        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=str(e),
            )

    def _extract_from_file(
        self, source: FileVideoSource, config: OutputConfig
    ) -> ExtractionResult:
        """Extract audio from a local video file using ffmpeg."""
        config.output_dir.mkdir(parents=True, exist_ok=True)
        src = source.get_source_identifier()
        stem = Path(src).stem
        safe_stem = "".join(c for c in stem if c.isalnum() or c in " -_")[:200]
        output_path = config.output_dir / f"{safe_stem}.{config.format}"

        # ffmpeg codec and quality
        codec_map = {"mp3": "libmp3lame", "m4a": "aac", "opus": "libopus"}
        codec = codec_map.get(config.format, "libmp3lame")
        if config.format == "mp3":
            quality = ["-q:a", "2"]
        else:
            quality = ["-b:a", "128k"]

        try:
            cmd = [
                "ffmpeg", "-y", "-i", src, "-vn", "-acodec", codec,
                *quality,
                str(output_path),
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                err = (result.stderr or result.stdout or "").strip().split("\n")[-1]
                return ExtractionResult(
                    success=False,
                    error_message=err or "ffmpeg failed",
                )
            return ExtractionResult(
                success=True,
                output_path=output_path,
                metadata={"title": safe_stem},
            )
        except FileNotFoundError:
            return ExtractionResult(
                success=False,
                error_message="ffmpeg not found. Install ffmpeg to extract from video files.",
            )
        except subprocess.TimeoutExpired:
            return ExtractionResult(
                success=False,
                error_message="Extraction timed out",
            )
        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=str(e),
            )

    def _get_output_path(self, info: dict, config: OutputConfig) -> Path | None:
        """Get the output file path from yt-dlp info or construct it."""
        requested = info.get("requested_downloads")
        if requested and requested[0].get("filepath"):
            return Path(requested[0]["filepath"])

        title = info.get("title", "audio")
        sanitized = "".join(c for c in title if c.isalnum() or c in " -_")[:200]
        return config.output_dir / f"{sanitized}.{config.format}"
