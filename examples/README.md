# Client configs

Copy the file for your client. Every one points at the same hosted server, `https://api.autojobs.me/api/v1/mcp`, and signs in with OAuth in your browser. None of them holds a key or password.

| Client | File | Where it goes |
| --- | --- | --- |
| Claude Code | [claude-code.sh](claude-code.sh) | Run it, or run the commands yourself |
| Cursor | [cursor/mcp.json](cursor/mcp.json) | `~/.cursor/mcp.json` or `.cursor/mcp.json` in a project |
| VS Code with GitHub Copilot | [vscode/mcp.json](vscode/mcp.json) | `.vscode/mcp.json` in a project, or your user MCP configuration |
| Codex | [codex/config.toml](codex/config.toml) | Add to `~/.codex/config.toml`, then run `codex mcp login tsenta` |
| OpenClaw | [openclaw/connect.sh](openclaw/connect.sh) | Run it, or run the commands yourself |
| Clients that only run local servers | [mcp-remote/mcp.json](mcp-remote/mcp.json) | Your client's MCP config. Needs Node.js. |

Claude on the web, Claude Desktop and ChatGPT are set up in their own settings pages, not with a file. See the [setup steps](../README.md#setup).
