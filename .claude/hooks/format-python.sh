#!/bin/bash
# Auto-format Python files after Write or Edit operations
# Based on Boris Cherny's lesson: handle the last 10% to avoid formatting errors in CI

# Read the tool input from stdin
file_path=$(jq -r '.tool_input.file_path' 2>/dev/null)

# Only process Python files
if [[ ! "$file_path" =~ \.py$ ]]; then
  exit 0
fi

# Check if file exists
if [[ ! -f "$file_path" ]]; then
  exit 0
fi

# Use ruff (recommended - faster, modern)
if command -v ruff &> /dev/null; then
  ruff format --quiet "$file_path" 2>/dev/null
  exit 0
fi

# Fall back to black
if command -v black &> /dev/null; then
  black --quiet "$file_path" 2>/dev/null
  exit 0
fi

# No formatter available - exit gracefully (don't block the operation)
exit 0
