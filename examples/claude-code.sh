#!/usr/bin/env sh
# Add Tsenta to Claude Code for every project, then sign in. Safe to run again.
set -e
claude mcp get tsenta >/dev/null 2>&1 ||
  claude mcp add --scope user --transport http tsenta https://api.autojobs.me/api/v1/mcp
claude mcp login tsenta          # approve in your browser
claude mcp list
