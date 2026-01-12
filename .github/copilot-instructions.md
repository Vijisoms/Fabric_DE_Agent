# Copilot instructions (repo-wide)

## What this repo is
- Python **MCP server** for Microsoft Fabric Data Engineering automation, built with `mcp.server.fastmcp.FastMCP`.
- Exposes MCP tools over the `streamable-http` transport (see `src/fabric_de_mcp/server.py`).

## Documentation
- Canonical docs live in `docs/`.
- Keep root `README.md` concise and task-focused (quickstart + common workflows) and link into `docs/index.md` for deeper detail.
- When adding/changing diagrams, use Mermaid and keep them consistent with the actual code paths.
- Prefer Mermaid `classDef` styles and HTML-friendly labels (e.g., `<br/>`) for readability.

## Repo structure (enforced)

If you notice files in the wrong place (especially `.env` files, requirements, or DevUI folders), prefer fixing the directory structure rather than working around it.

- This is a `src/` layout repo.
- MCP server code lives under `src/fabric_de_mcp/`.
- DevUI code lives under `src/devui/`.
- Canonical structure documentation: `docs/folder-structure.md`.

## Where to change code
- Prefer editing production code under `src/fabric_de_mcp/` (src-layout packaging).
- Tool registration + CLI entrypoint: `src/fabric_de_mcp/server.py` (uses `@app.tool()` and `app.run(...)`).
- HTTP + payload construction + retries: `src/fabric_de_mcp/fabric/api.py` (uses `requests` + `Retry`).
- Auth: `src/fabric_de_mcp/fabric/auth.py` (uses `azure.identity.DefaultAzureCredential`).
- Config/env vars: `src/fabric_de_mcp/config.py` (`FABRIC_BASE_URL`, `FABRIC_SCOPE`).

## DevUI (local testing)
- DevUI agent(s) live under `src/devui/`.
- Directory discovery expects each agent folder to export `agent` from `__init__.py` (implementation in `agent.py`).
- DevUI uses `MCPStreamableHTTPTool` to call the MCP server at `MCP_SERVER_URL`.

### DevUI + deployed MCP
- The MCP endpoint path is always `/mcp`.
- Local default is `http://127.0.0.1:8000/mcp`.
- For Azure Container Apps, use `https://<containerapp-fqdn>/mcp` (never hard-code real FQDNs in tracked files).

## MCP tool stability
- Keep MCP tool **names and parameter schemas stable** (they are the public API). Avoid renames and breaking parameter changes.
- Tool wrappers accept an optional `token` override; otherwise use `get_token()`.

Current tool surface area includes (non-exhaustive):
- create_item / update_item / list_items / get_item
- create_pipeline / run_pipeline_job_instance / get_pipeline_job_instance
- create_lakehouse / get_lakehouse / list_lakehouse_tables
- list_workspaces

## Error + retry pattern
- Use `build_session(retries, backoff)` from `fabric/api.py` for outbound HTTP.
- On non-success status, raise `FabricApiError(status_code, body)`; return `resp.json()` on success.

## Local workflows
- Run: `python -m fabric_de_mcp` or `fab-de-mcp --transport streamable-http`.
- Tests: `pytest`.
- Lint: `ruff check .` (installed via `requirements-dev.txt`).

## Environment files (.env)

This repo keeps env files **per app**. When running locally, first confirm the `.env` files exist; if not, create them from the corresponding `.env.example`.

### Check whether `.env` files exist (PowerShell)

- MCP server:
	- `Test-Path src/fabric_de_mcp/.env`
- DevUI agent:
	- `Test-Path src/devui/fabric_de_agent/.env`

### Create missing `.env` files from examples (PowerShell)

- MCP server:
	- `Copy-Item src/fabric_de_mcp/.env.example src/fabric_de_mcp/.env`
- DevUI agent:
	- `Copy-Item src/devui/fabric_de_agent/.env.example src/devui/fabric_de_agent/.env`

After copying, edit the new `.env` file(s) and fill in required values.

### Misplaced `.env` files (detect + correct)

Some developers may have `.env` files in other locations. If expected `.env` files are missing, search the repo to see if they exist elsewhere and move them into the correct per-app directories.

PowerShell (from repo root):

- Find env files (do not print contents):
	- `Get-ChildItem -Recurse -Force -File -Filter .env* | Select-Object FullName`

Expected locations:

- MCP server:
	- `src/fabric_de_mcp/.env`
	- `src/fabric_de_mcp/.env.example`
- DevUI agent:
	- `src/devui/fabric_de_agent/.env`
	- `src/devui/fabric_de_agent/.env.example`

If you find an env file in the wrong place:

- Move it to the correct location (preserve contents) and remove duplicates.
- Do not add new “fallback” env loading from repo root; keep env files app-scoped.
- Never commit `.env` files.

## Azure deployment (azd)
- This repo is configured for Azure Developer CLI (`azd`) via `azure.yaml` and `infra/`.
- Deploy with:
	- `az login`
	- `azd up`
- Retrieve the deployed Container App FQDN from outputs:
	- `azd env get-values` (look for `CONTAINER_APP_FQDN`)
- Use `https://<CONTAINER_APP_FQDN>/mcp` as the deployed MCP URL.

## Security
- Never commit or log bearer tokens/keys. Prefer `DefaultAzureCredential` and local `.env` (git-ignored).
- Do not add diagrams or docs containing real tenant IDs, subscription IDs, endpoints, or hostnames. Use placeholders.

### No sensitive info in commits
- Do not hard-code any environment-specific identifiers (project endpoints, subscription IDs, resource group names, hostnames) in tracked files.
	- Use placeholders (e.g., `https://<resource>.services.ai.azure.com/...`, `https://<containerapp-fqdn>/mcp`) and/or environment variables.
- Never commit local azd state or environment outputs (anything under `.azure/`).
- Before committing changes that touch auth, endpoints, or configuration, quickly scan what’s staged:
	- `git diff --cached`
	- `git grep -n -I "AZURE_\|SUBSCRIPTION\|TENANT\|CLIENT_SECRET\|PRIVATE KEY\|Bearer " -- .`

### Keep `.gitignore` current
- When adding scripts, configs, or samples that may contain secrets or environment-specific values, update `.gitignore` in the same PR.
- Prefer checked-in templates like `.env.example` and keep real values in local `.env` (already ignored).

## VS Code Copilot assets
- Put custom agents/prompts/instructions under `.github/agents/`, `.github/prompts/`, `.github/instructions/`.
