# mlx-transcribe

Fast, local transcription for 1700+ sites (YouTube, X/Twitter, TikTok, Instagram, Vimeo, etc.) using mlx-whisper.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Video URL  │ ──▶ │   yt-dlp    │ ──▶ │  mlx-whisper │ ──▶ Transcript
│  (any site) │     │  (download) │     │ (transcribe) │
└─────────────┘     └─────────────┘     └──────────────┘
```

**Apple Silicon Optimized**: mlx-whisper uses native Metal GPU acceleration on M-series chips.

## Components

| Component | Purpose | Why It's Stable |
|-----------|---------|-----------------|
| **yt-dlp** | Video download | Active development, 1700+ site support, community maintained |
| **mlx-whisper** | Transcription | Native Metal GPU acceleration on Apple Silicon |

## Prerequisites

- **Apple Silicon Mac** (M1/M2/M3/etc.) — mlx-whisper requires Metal; Intel Macs are not supported
- **uv** ([install](https://docs.astral.sh/uv/getting-started/installation/)) — Python 3.11+ is installed automatically if you don't have it

## Installation

```bash
uv tool install .
```

## Usage

```bash
# Works with any supported site
transcribe "https://www.youtube.com/watch?v=..."
transcribe "https://x.com/user/status/123456789"

# Options
transcribe "URL" --whisper-model medium --language en --output transcript.txt

# Copy transcript to clipboard, then paste into your favorite LLM
transcribe "URL" | pbcopy
```

## Whisper Model Selection

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | 39M | Fastest | Lower | Quick drafts |
| `base` | 74M | Fast | Good | Balanced |
| `small` | 244M | Medium | Better | Most videos |
| `medium` | 769M | Slow | High | Important content |
| `large` | 1.5G | Slowest | Highest | Critical accuracy |
| `large-v3` | 1.5G | Slowest | Best | **Default**, latest model, best accuracy |

## Troubleshooting

### Download Fails

If yt-dlp can't download directly:

1. **Update dependencies**: `uv sync`
2. **Try with cookies**: The script automatically tries browser cookies if direct download fails
3. **Check if video is public**: Private/protected videos cannot be downloaded

### Whisper is Slow

- Use a smaller model: `--whisper-model tiny`
- Ensure you have enough RAM (large model needs ~10GB)

### No Audio in Video

Some X posts are GIFs or silent videos. The script will still try to process them but transcription will be empty.

## API Usage (Python)

```python
from mlx_transcribe import process_url

# Returns transcript as a string
transcript = process_url(
    url="https://www.youtube.com/watch?v=...",
    whisper_model="large-v3",
    language="en",
    output_file=None  # Optional: save to file
)

print(transcript)
```

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
