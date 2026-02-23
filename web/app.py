"""Minimal Flask server for the audio extractor web UI."""

import sys
import tempfile
from pathlib import Path

# Allow importing audio_extracter when run from web/ (e.g. python app.py)
_web_dir = Path(__file__).resolve().parent
_project_root = _web_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from flask import Flask, jsonify, render_template, request

from audio_extracter import AudioExtractor, FileVideoSource, LinkVideoSource, OutputConfig

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)

# Output directory for extracted audio (project root / output)
OUTPUT_DIR = _project_root / "output"


@app.get("/")
def index():
    """Serve the main page with the link input layout."""
    return render_template("index.html")


@app.post("/api/extract")
def extract():
    """Run extraction for a URL, same logic as main.py. Expects JSON: { \"url\": \"...\" }."""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"success": False, "error_message": "No URL provided"}), 400

    source = LinkVideoSource(url)
    config = OutputConfig(
        format="mp3",
        output_dir=OUTPUT_DIR,
        filename_template="%(title)s.%(ext)s",
    )
    extractor = AudioExtractor()
    result = extractor.extract(source, config)

    if result.success:
        return jsonify({
            "success": True,
            "output_path": str(result.output_path),
            "metadata": result.metadata or {},
        })
    return jsonify({
        "success": False,
        "error_message": result.error_message or "Extraction failed",
    }), 422


@app.post("/api/extract-file")
def extract_file():
    """Extract audio from an uploaded video file. Expects multipart form with 'file'."""
    upload = request.files.get("file")
    if not upload or upload.filename == "":
        return jsonify({"success": False, "error_message": "No file provided"}), 400

    suffix = Path(upload.filename).suffix
    if suffix.lower() not in {
        ".mp4", ".m4v", ".webm", ".mkv", ".avi", ".mov", ".flv", ".wmv",
        ".ogv", ".3gp", ".mpeg", ".mpg", ".ts", ".m2ts",
    }:
        return jsonify({
            "success": False,
            "error_message": "Unsupported format. Use a video file (e.g. mp4, webm, mkv).",
        }), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload.read())
            tmp_path = Path(tmp.name)
    except Exception as e:
        return jsonify({"success": False, "error_message": str(e)}), 500

    try:
        source = FileVideoSource(tmp_path)
        config = OutputConfig(
            format="mp3",
            output_dir=OUTPUT_DIR,
            filename_template="%(title)s.%(ext)s",
        )
        extractor = AudioExtractor()
        result = extractor.extract(source, config)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass

    if result.success:
        return jsonify({
            "success": True,
            "output_path": str(result.output_path),
            "metadata": result.metadata or {},
        })
    return jsonify({
        "success": False,
        "error_message": result.error_message or "Extraction failed",
    }), 422


if __name__ == "__main__":
    app.run(debug=True, port=5001)
