# Claude Code Setup Summary

## Three-Tier Configuration

### 1️⃣ User-level: `~/.claude/settings.json`
**Scope:** ALL your projects
**Commit:** No (personal machine settings)

```json
{
  "permissions": {
    "allow": [
      "Bash(cd:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(grep:*)", ...
      "Bash(git status)", "Bash(git log:*)", "Bash(git diff:*)", ...
      "Bash(python --version)", "Bash(python -m:*)", ...
    ]
  }
}
```

**What's here:** Safe commands that work in ANY project:
- File navigation and inspection
- Read-only git commands
- Version checks
- Basic Python commands

### 2️⃣ Project-level: `.claude/settings.json`
**Scope:** This project only
**Commit:** ✅ Yes (share with team)

```json
{
  "permissions": {
    "allow": [
      "Bash(uv run python:*)",
      "Bash(uv sync)",
      "Bash(ruff check:*)",
      "Bash(ruff format:*)",
      "Bash(yt-dlp --version)"
    ]
  }
}
```

**What's here:** Tools specific to THIS transcriber project:
- `uv` - This project's package manager
- `ruff` - This project's formatter
- `yt-dlp` - This project's video downloader

### 3️⃣ Local: `.claude/settings.local.json`
**Scope:** This project on YOUR machine
**Commit:** ❌ No (gitignored)

```json
{
  "hooks": {
    "PostToolUse": [...]
  }
}
```

**What's here:** Personal machine-specific settings:
- Hooks (auto-format on save)
- Personal overrides

## Benefits of This Setup

✅ **Reusable:** Common permissions work across all projects
✅ **Shareable:** Team gets project-specific permissions
✅ **Personal:** Your hooks and overrides stay private
✅ **No prompts:** Most operations are pre-approved

## What Gets Committed

```
.claude/
├── README.md              ✅ Commit (documentation)
├── SETUP_SUMMARY.md       ✅ Commit (this file)
├── settings.json          ✅ Commit (project permissions)
├── settings.local.json    ❌ NO (gitignored, personal)
└── hooks/
    └── format-python.sh   ✅ Commit (team hook)
```

## Quick Reference

| Command Type | User-level | Project-level | Example |
|-------------|-----------|--------------|---------|
| File ops | ✅ | | `ls`, `cat`, `grep` |
| Git (read) | ✅ | | `git status`, `git diff` |
| Git (write) | ❌ | ❌ | `git add` (requires approval) |
| Python basic | ✅ | | `python --version` |
| Python run | | ✅ | `uv run python` |
| Formatting | | ✅ | `ruff format` |

## Testing

Run in Claude Code:
```
/permissions
```

You should see permissions from both user-level AND project-level merged together.
