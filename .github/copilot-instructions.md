# Copilot instructions (repo-wide)

## What this repo is
- Python **MCP server** for Microsoft Fabric Data Engineering automation, built with `mcp.server.fastmcp.FastMCP`.
- Exposes a small set of tools (currently `create_lakehouse`, `create_pipeline`) over the `streamable-http` transport.

## Where to change code
- Prefer editing production code under `src/fabric_de_mcp/` (src-layout packaging).
- Tool registration + CLI entrypoint: `src/fabric_de_mcp/server.py` (uses `@app.tool()` and `app.run(...)`).
- HTTP + payload construction + retries: `src/fabric_de_mcp/fabric/api.py` (uses `requests` + `Retry`).
- Auth: `src/fabric_de_mcp/fabric/auth.py` (uses `azure.identity.DefaultAzureCredential`).
- Config/env vars: `src/fabric_de_mcp/config.py` (`FABRIC_BASE_URL`, `FABRIC_SCOPE`).

## MCP tool stability
- Keep MCP tool **names and parameter schemas stable** (they are the public API). Avoid renames and breaking parameter changes.
- Tool wrappers accept an optional `token` override; otherwise use `get_token()`.

## Error + retry pattern
- Use `build_session(retries, backoff)` from `fabric/api.py` for outbound HTTP.
- On non-success status, raise `FabricApiError(status_code, body)`; return `resp.json()` on success.

## Local workflows
- Run: `python -m fabric_de_mcp` or `fab-de-mcp --transport streamable-http`.
- Tests: `pytest`.
- Lint: `ruff check .` (installed via `requirements-dev.txt`).

## Security
- Never commit or log bearer tokens/keys. Prefer `DefaultAzureCredential` and local `.env` (git-ignored).

## VS Code Copilot assets
- Put custom agents/prompts/instructions under `.github/agents/`, `.github/prompts/`, `.github/instructions/`.
