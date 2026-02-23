#!/usr/bin/env python3
"""Extract audio from video URLs. Use from the command line."""

import argparse
from pathlib import Path

from audio_extracter import AudioExtractor, LinkVideoSource, OutputConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract audio from video URLs (YouTube, Vimeo, etc.)",
    )
    parser.add_argument(
        "url",
        help="Video URL to extract audio from",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("./output"),
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["mp3", "m4a", "opus"],
        default="mp3",
        help="Output audio format (default: mp3)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    source = LinkVideoSource(args.url)
    config = OutputConfig(
        format=args.format,
        output_dir=args.output,
        filename_template="%(title)s.%(ext)s",
    )

    print(f"Extracting audio from: {args.url}")
    print(f"Output: {config.output_dir}/ ({args.format})\n")

    extractor = AudioExtractor()
    result = extractor.extract(source, config)

    if result.success:
        print(f"Done! Saved to: {result.output_path}")
        if result.metadata:
            print(f"Title: {result.metadata.get('title', 'N/A')}")
            print(f"Duration: {result.metadata.get('duration', 'N/A')}s")
    else:
        print(f"Failed: {result.error_message}")


if __name__ == "__main__":
    main()
