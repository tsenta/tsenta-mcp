#!/usr/bin/env sh
# Connect Tsenta to OpenClaw. OpenClaw's MCP commands run while the Gateway is stopped.
# The Gateway is started again at the end, even if a step fails. Safe to run again:
# `mcp set` creates the server entry or replaces it.
set -e
openclaw gateway stop
trap 'openclaw gateway start' EXIT
trap 'exit 130' INT TERM HUP
openclaw mcp set tsenta '{"url":"https://api.autojobs.me/api/v1/mcp","transport":"streamable-http","auth":"oauth"}'
openclaw mcp login tsenta        # open the printed link and approve
openclaw mcp doctor tsenta --probe
