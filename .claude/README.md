# Claude Code Configuration

This directory contains Claude Code configuration for the project.

## Settings Hierarchy

Claude Code uses a three-tier settings system:

1. **User-level** (`~/.claude/settings.json`) - Applies to ALL your projects
   - Common safe commands (cd, ls, cat, grep, git status, etc.)
   - Personal preferences that work everywhere

2. **Project-level** (`.claude/settings.json`) - This project only
   - Project-specific tools: `uv`, `ruff`, `yt-dlp`
   - **Commit this** to share with team

3. **Local** (`.claude/settings.local.json`) - Your machine only
   - Personal overrides and hooks
   - **Do NOT commit** - in `.gitignore`

## Files

### `settings.json` (Project-level, team-shared)
Pre-approved commands **specific to this project**.

**Current permissions:**
- **uv**: Package management (`uv sync`, `uv run python`, etc.)
- **ruff**: Code formatting and linting
- **yt-dlp**: Version checks

### `settings.local.json` (Local-only)
Personal settings specific to your machine.
**Do NOT commit** - in `.gitignore`.

Currently contains:
- PostToolUse hooks for auto-formatting

### `hooks/` (Team-shared)
Executable scripts for Claude Code hooks.

**Current hooks:**
- `format-python.sh`: Auto-format Python files after Write/Edit using `ruff`

## Philosophy

Following [Boris Cherny's approach](https://x.com/bcherny/status/1871660614593290684):

1. **Pre-allow safe commands** - Avoid permission prompt fatigue
2. **Share with team** - Check `settings.json` into git
3. **Keep it focused** - Only commands safe in this project's context
4. **Document reasoning** - This README explains why each permission exists

## Adding New Permissions

Before adding a permission, ask:
1. Is this command **read-only** or **reversible**?
2. Is it **scoped** to this project directory?
3. Would a teammate expect this to be safe?
4. Can it **leak** sensitive data or **modify** critical files?

If yes to 1-3 and no to 4, add it to `settings.json`.

## Testing

Run `/permissions` in Claude Code to see the current configuration.
