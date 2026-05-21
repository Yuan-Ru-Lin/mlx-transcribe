# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file Python CLI tool that transcribes video/audio from 1700+ sites (YouTube, X/Twitter, TikTok, etc.) using a two-stage pipeline: **yt-dlp** (download) -> **mlx-whisper** (transcription with Metal GPU acceleration on Apple Silicon, decodes audio internally via the bundled `ffmpeg` from `imageio-ffmpeg`).

All logic lives in `mlx_transcribe.py`. The entry point is `main()`, and the programmatic API is `process_url()`.

## Commands

```bash
# Install as a global tool
uv tool install .

# Run transcription (default model: small)
transcribe "URL"
transcribe "URL" --whisper-model small --language en --output transcript.txt

# Lint and format
ruff check mlx_transcribe.py
ruff format mlx_transcribe.py
```

## Architecture

- `mlx_transcribe.py` — entire application in one file, three main functions:
  - `download_video()` — uses yt-dlp Python API, falls back to browser cookies on failure
  - `transcribe_audio()` — runs mlx-whisper with Metal acceleration, model from `mlx-community/whisper-{model}-mlx`. Adds the bundled `imageio-ffmpeg` binary to `PATH` so mlx-whisper's internal `subprocess.run(["ffmpeg", ...])` resolves to it.
  - `process_url()` — orchestrates the pipeline in a temp directory, optionally saves to file
- All status/progress output goes to **stderr**; only the final transcript goes to **stdout** (pipe-friendly design)
- Uses `tempfile.TemporaryDirectory` for intermediate files — no cleanup needed

## Key Dependencies

- **mlx-whisper** — Apple Silicon only (Metal GPU). Not compatible with non-Apple hardware.
- **yt-dlp** — used as a Python library (not subprocess)
- **imageio-ffmpeg** — ships the `ffmpeg` CLI binary that mlx-whisper shells out to for audio decode

## Claude Code Configuration

- `.claude/settings.json` — pre-approved bash commands for uv, ruff, and yt-dlp
- `.claude/hooks/format-python.sh` — auto-formats `.py` files with ruff after Write/Edit operations
- `AGENTS.md` — workflow guidelines: plan mode for non-trivial tasks, use subagents for research, track lessons in `tasks/lessons.md`
