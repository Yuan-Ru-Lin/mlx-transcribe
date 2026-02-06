#!/usr/bin/env python3
"""
Transcriber

Fast local transcription for 1700+ sites (YouTube, X/Twitter, TikTok, etc.)

Pipeline:
1. Downloads video using yt-dlp (supports 1700+ sites)
2. Extracts audio using PyAV
3. Transcribes using mlx-whisper (native Metal GPU on Apple Silicon)

Requirements:
    uv sync  # Install all dependencies

Usage:
    # Basic usage
    uv run python transcriber.py "https://www.youtube.com/watch?v=..."

    # Pipe to Claude Code for summarization
    uv run python transcriber.py "URL" | claude -p "Summarize this video transcript"
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def check_dependencies():
    """Check if required tools are installed."""
    missing = []

    # Check yt-dlp
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("yt-dlp (uv sync)")

    # Check PyAV
    try:
        import av
    except ImportError:
        missing.append("av (uv sync)")

    # Check mlx-whisper
    try:
        import mlx_whisper
    except ImportError:
        missing.append("mlx-whisper (uv sync)")

    if missing:
        print("Missing dependencies:", file=sys.stderr)
        for dep in missing:
            print(f"  - {dep}", file=sys.stderr)
        if any(
            dep.startswith(name)
            for dep in missing
            for name in ["yt-dlp", "av", "mlx-whisper"]
        ):
            sys.exit(1)


def download_video(url: str, output_dir: str) -> str:
    """
    Download video from X/Twitter using yt-dlp.

    Args:
        url: The X/Twitter post URL
        output_dir: Directory to save the video

    Returns:
        Path to the downloaded video file
    """
    output_template = os.path.join(output_dir, "video.%(ext)s")

    cmd = [
        "yt-dlp",
        "--no-warnings",
        "-f",
        "best[ext=mp4]/best",  # Prefer mp4, fallback to best
        "-o",
        output_template,
        "--no-playlist",
        url,
    ]

    print(f"Downloading video from: {url}", file=sys.stderr)
    # Don't capture stderr so yt-dlp's progress bar is visible
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)

    if result.returncode != 0:
        # Try alternative method with cookies if direct download fails
        print("Direct download failed, trying with browser cookies...", file=sys.stderr)
        cmd_with_cookies = cmd + ["--cookies-from-browser", "firefox"]
        result = subprocess.run(cmd_with_cookies, stdout=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise RuntimeError("Failed to download video")

    # Find the downloaded file
    for ext in ["mp4", "webm", "mkv", "mov"]:
        video_path = os.path.join(output_dir, f"video.{ext}")
        if os.path.exists(video_path):
            print(f"Downloaded: {video_path}", file=sys.stderr)
            return video_path

    raise RuntimeError("Video file not found after download")


def extract_audio(video_path: str, output_dir: str) -> str:
    """
    Extract audio from video using PyAV.

    Args:
        video_path: Path to the video file
        output_dir: Directory to save the audio

    Returns:
        Path to the extracted audio file
    """
    import av

    audio_path = os.path.join(output_dir, "audio.mp3")

    print("Extracting audio...", file=sys.stderr)

    # Open input video
    input_container = av.open(video_path)
    audio_stream = next((s for s in input_container.streams if s.type == "audio"), None)

    if not audio_stream:
        raise RuntimeError("No audio stream found in video")

    # Resample audio to 16kHz mono first
    resampler = av.audio.resampler.AudioResampler(
        format="s16", layout="mono", rate=16000
    )

    # Open output file
    output_container = av.open(audio_path, "w")
    output_stream = output_container.add_stream("mp3", rate=16000, layout="mono")

    # Process audio frames
    for frame in input_container.decode(audio_stream):
        resampled_frames = resampler.resample(frame)
        for resampled_frame in resampled_frames:
            for packet in output_stream.encode(resampled_frame):
                output_container.mux(packet)

    # Flush remaining packets
    for packet in output_stream.encode():
        output_container.mux(packet)

    # Close containers
    input_container.close()
    output_container.close()

    print(f"Audio extracted: {audio_path}", file=sys.stderr)
    return audio_path


def transcribe_audio(
    audio_path: str, model_name: str = "base", language: str = None
) -> str:
    """
    Transcribe audio using mlx-whisper (native Metal acceleration on Apple Silicon).

    Args:
        audio_path: Path to the audio file
        model_name: Whisper model size (tiny, base, small, medium, large, large-v3)
        language: Language code (e.g., 'en', 'zh') or None for auto-detect

    Returns:
        Transcribed text
    """
    import mlx_whisper

    print(f"Loading Whisper model: {model_name}", file=sys.stderr)
    print("Transcribing audio (using Metal GPU)...", file=sys.stderr)

    # mlx-whisper uses Metal acceleration automatically on Apple Silicon
    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo=f"mlx-community/whisper-{model_name}-mlx",
        language=language,
        verbose=False,
    )

    transcript = result["text"].strip()
    detected_lang = result.get("language", "unknown")
    print(f"Detected language: {detected_lang}", file=sys.stderr)
    print(f"Transcription complete ({len(transcript)} characters)", file=sys.stderr)

    return transcript


def process_url(
    url: str, whisper_model: str = "base", language: str = None, output_file: str = None
) -> str:
    """
    Complete pipeline: download → extract → transcribe.

    Args:
        url: X/Twitter video URL
        whisper_model: Whisper model size
        language: Language code or None for auto-detect
        output_file: Optional file to save transcript

    Returns:
        Transcribed text
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Step 1: Download video
        video_path = download_video(url, temp_dir)

        # Step 2: Extract audio
        audio_path = extract_audio(video_path, temp_dir)

        # Step 3: Transcribe
        transcript = transcribe_audio(audio_path, whisper_model, language)

        # Save to file if requested
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"\nTranscript saved to: {output_file}", file=sys.stderr)

        return transcript


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe videos from 1700+ sites (YouTube, X, TikTok, etc.)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage
    uv run python transcriber.py "https://www.youtube.com/watch?v=..."
    uv run python transcriber.py "https://x.com/user/status/123456789"

    # With options
    uv run python transcriber.py "URL" --whisper-model small --language en

    # Pipe to Claude Code for summarization (use -p flag)
    uv run python transcriber.py "URL" | claude -p "Summarize this video transcript"
        """,
    )

    parser.add_argument("url", nargs="?", help="Video URL from any supported site")
    parser.add_argument(
        "--whisper-model",
        "-m",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "large-v3"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--language",
        "-l",
        default=None,
        help="Language code (e.g., 'en', 'zh'). Auto-detect if not specified",
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Output file to save transcript"
    )
    parser.add_argument(
        "--check-deps", action="store_true", help="Check dependencies and exit"
    )

    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    if args.check_deps:
        print("All required dependencies are installed!")
        return

    # Ensure URL is provided
    if not args.url:
        parser.error("the following arguments are required: url")

    # Process the URL
    transcript = process_url(
        url=args.url,
        whisper_model=args.whisper_model,
        language=args.language,
        output_file=args.output,
    )

    # Print transcript to stdout (pipe-friendly)
    print(transcript)


if __name__ == "__main__":
    main()
