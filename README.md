# Transcriber

Fast, local transcription for 1700+ sites (YouTube, X/Twitter, TikTok, Instagram, Vimeo, etc.) using faster-whisper.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│ Video URL   │ ──▶ │   yt-dlp    │ ──▶ │    PyAV     │ ──▶ │faster-whisper│ ──▶ Transcript
│  (any site) │     │  (download) │     │  (extract)  │     │ (transcribe) │
└─────────────┘     └─────────────┘     └─────────────┘     └──────────────┘
```

**Apple Silicon Optimized**: mlx-whisper uses native Metal GPU acceleration on M-series chips.

## Components

| Component | Purpose | Why It's Stable |
|-----------|---------|-----------------|
| **yt-dlp** | Video download | Active development, 1700+ site support, community maintained |
| **PyAV** | Audio extraction | Python bindings to FFmpeg libraries, well-maintained |
| **mlx-whisper** | Transcription | Native Metal GPU acceleration on Apple Silicon |

## Prerequisites

- uv (Python package manager)

## Installation

```bash
uv sync
```

## Usage

### Basic Usage

```bash
# Works with any supported site
uv run python transcriber.py "https://www.youtube.com/watch?v=..."
uv run python transcriber.py "https://x.com/user/status/123456789"
uv run python transcriber.py "https://www.tiktok.com/@user/video/..."
```

### Pipe to Claude Code for Summarization

Since you have Claude Pro, pipe the transcript directly to Claude Code:

```bash
# Summarize the video
uv run python transcriber.py "URL" | claude -p "Summarize this video transcript"

# Extract key points
uv run python transcriber.py "URL" | claude -p "What are the main points?"

# Translate
uv run python transcriber.py "URL" | claude -p "Translate to Spanish"
```

**Note**: The `-p` flag runs Claude in non-interactive mode for piping.

### Options

```bash
# Use a larger Whisper model for better accuracy
uv run python transcriber.py "URL" --whisper-model medium

# Specify language (faster transcription)
uv run python transcriber.py "URL" --language en

# Save transcript to file
uv run python transcriber.py "URL" --output transcript.txt
```

### Create an Alias

```bash
# Add to ~/.zshrc or ~/.bashrc
alias transcribe="uv run --directory ~/path/to/transcriber python transcriber.py"

# Then use it:
transcribe "URL" | claude -p "Summarize this"
```

## Whisper Model Selection

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | 39M | Fastest | Lower | Quick drafts |
| `base` | 74M | Fast | Good | **Default, balanced** |
| `small` | 244M | Medium | Better | Most videos |
| `medium` | 769M | Slow | High | Important content |
| `large` | 1.5G | Slowest | Highest | Critical accuracy |
| `large-v3` | 1.5G | Slowest | Best | Latest model, best accuracy |

## Troubleshooting

### Download Fails

If yt-dlp can't download directly:

1. **Update dependencies**: `uv sync`
2. **Try with cookies**: The script automatically tries browser cookies if direct download fails
3. **Check if video is public**: Private/protected videos cannot be downloaded

### Whisper is Slow

- Use a smaller model: `--whisper-model tiny`
- Install CUDA for GPU acceleration
- Ensure you have enough RAM (large model needs ~10GB)

### No Audio in Video

Some X posts are GIFs or silent videos. The script will still try to process them but transcription will be empty.

## API Usage (Python)

```python
from transcriber import process_url

# Returns transcript as a string
transcript = process_url(
    url="https://www.youtube.com/watch?v=...",
    whisper_model="base",
    language="en",
    output_file=None  # Optional: save to file
)

print(transcript)
```

## Alternatives

If this pipeline doesn't work for your use case:

- **Web-based**: [VMEG](https://vmeg.ai/tools/transcribe-twitter-video/)
- **GUI**: [Tartube](https://github.com/axcore/tartube) (yt-dlp frontend)
- **API**: [Supadata Twitter Transcript API](https://supadata.ai/twitter-transcript-api)

## Claude Code Integration

This project includes Claude Code configuration for enhanced development workflow:

- **Pre-approved permissions** - Safe bash commands are pre-allowed to avoid prompt fatigue
- **Auto-formatting hook** - Python files are automatically formatted after editing
- See [`.claude/README.md`](.claude/README.md) for details

To use:
1. Open this directory in Claude Code
2. Permissions and hooks are automatically applied
3. Run `/permissions` to see the configuration

## License

MIT License - Use freely for personal and commercial projects.
