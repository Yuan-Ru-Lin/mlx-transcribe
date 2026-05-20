#!/usr/bin/env python3
"""
mlx-transcribe

Fast local transcription for 1700+ sites (YouTube, X/Twitter, TikTok, etc.)

Pipeline:
1. Downloads video using yt-dlp (supports 1700+ sites)
2. Transcribes using mlx-whisper (native Metal GPU on Apple Silicon)

Requirements:
    uv sync  # Install all dependencies

Usage:
    # Basic usage
    uv run python mlx_transcribe.py "https://www.youtube.com/watch?v=..."

    # Pipe to Claude Code for summarization
    uv run python mlx_transcribe.py "URL" | claude -p "Summarize this video transcript"
"""

import argparse
import os
import sys
import tempfile


def download_video(url: str, output_dir: str) -> str:
    """
    Download video using yt-dlp Python API.

    Args:
        url: Video URL from any supported site
        output_dir: Directory to save the video

    Returns:
        Path to the downloaded video file
    """
    import yt_dlp

    output_template = os.path.join(output_dir, "video.%(ext)s")

    opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "no_warnings": True,
        # TODO: Remove syndication workaround when fixed: https://github.com/yt-dlp/yt-dlp/issues/15963
        "extractor_args": {"twitter": {"api": ["syndication"]}},
    }

    print(f"Downloading video from: {url}", file=sys.stderr)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError:
        print("Direct download failed, trying with browser cookies...", file=sys.stderr)
        opts["cookiesfrombrowser"] = ("firefox",)
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    # Find the downloaded file
    for ext in ["mp4", "webm", "mkv", "mov"]:
        video_path = os.path.join(output_dir, f"video.{ext}")
        if os.path.exists(video_path):
            print(f"Downloaded: {video_path}", file=sys.stderr)
            return video_path

    raise RuntimeError("Video file not found after download")


def transcribe_audio(
    media_path: str, model_name: str = "large-v3", language: str = None
) -> str:
    """
    Transcribe media using mlx-whisper (native Metal acceleration on Apple Silicon).

    Args:
        media_path: Path to the media file (any container ffmpeg can read)
        model_name: Whisper model size (tiny, base, small, medium, large, large-v3)
        language: Language code (e.g., 'en', 'zh') or None for auto-detect

    Returns:
        Transcribed text
    """
    import subprocess

    import imageio_ffmpeg
    import mlx_whisper

    # mlx-whisper shells out to the "ffmpeg" CLI; ensure the bundled binary is on PATH.
    ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    if ffmpeg_dir not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

    # Fail fast on silent inputs so we don't load a 3GB model just to crash later.
    probe = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", media_path],
        capture_output=True,
        text=True,
    )
    has_audio = any(
        "Stream #" in line and "Audio:" in line for line in probe.stderr.splitlines()
    )
    if not has_audio:
        raise RuntimeError(
            f"No audio stream found in '{os.path.basename(media_path)}'. "
            "The source has no audio to transcribe."
        )

    print(f"Loading Whisper model: {model_name}", file=sys.stderr)
    print("Transcribing audio (using Metal GPU)...", file=sys.stderr)

    # mlx-whisper uses Metal acceleration automatically on Apple Silicon
    result = mlx_whisper.transcribe(
        media_path,
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
    url: str,
    whisper_model: str = "large-v3",
    language: str = None,
    output_file: str = None,
) -> str:
    """
    Complete pipeline: download → transcribe.

    Args:
        url: Video URL from any supported site
        whisper_model: Whisper model size
        language: Language code or None for auto-detect
        output_file: Optional file to save transcript

    Returns:
        Transcribed text
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Step 1: Download video
        video_path = download_video(url, temp_dir)

        # Step 2: Transcribe (mlx-whisper handles audio decode internally via ffmpeg)
        transcript = transcribe_audio(video_path, whisper_model, language)

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
    transcribe "https://www.youtube.com/watch?v=..."
    transcribe "https://x.com/user/status/123456789"

    # With options
    transcribe "URL" --whisper-model small --language en

    # Copy transcript to clipboard
    transcribe "URL" | pbcopy
        """,
    )

    parser.add_argument("url", nargs="?", help="Video URL from any supported site")
    parser.add_argument(
        "--whisper-model",
        "-m",
        default="large-v3",
        choices=["tiny", "base", "small", "medium", "large", "large-v3"],
        help="Whisper model size (default: large-v3)",
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
    args = parser.parse_args()

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
