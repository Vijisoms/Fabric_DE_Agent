# AGENTS

Agent-focused instructions for working on this repo (kept separate from `README.md`).

## Project overview

- This repo is a **Python MCP server** that wraps the Microsoft Fabric REST API for Data Engineering automation.
- The MCP surface area is defined by `@app.tool()` functions in `src/fabric_de_mcp/server.py`.
- There is also a **DevUI + Agent Framework** entrypoint for local testing under `src/devui/`.

## Docs (canonical)

- Start here: `docs/index.md`

## Setup (Windows / PowerShell)

- Create and activate venv:
  - `python -m venv .venv`
  - `.\.venv\Scripts\Activate.ps1`
- Install dependencies:
  - Dev/editable install: `python -m pip install -e .`
  - Dev tooling (tests + lint): `python -m pip install -r requirements-dev.txt`

## Run locally (MCP server)

- Module entrypoint: `python -m fabric_de_mcp`
- Console script: `fab-de-mcp --transport streamable-http`

The MCP endpoint is served at `/mcp` (default local URL: `http://127.0.0.1:8000/mcp`).

### MCP env file

- Check whether the env file exists:
  - `Test-Path src/fabric_de_mcp/.env`
- If missing, create it from the example:
  - `Copy-Item src/fabric_de_mcp/.env.example src/fabric_de_mcp/.env`

## Run locally (DevUI)

DevUI is for interactive testing of the MCP tool surface.

1. Install DevUI dependencies:

    - `python -m pip install --pre -r src/devui/requirements.txt`

1. Configure agent env vars:

    - Copy `src/devui/fabric_de_agent/.env.example` to `src/devui/fabric_de_agent/.env` and fill it in.
    - Set `FABRIC_DE_MCP_SERVER_URL` to your MCP server (default: `http://127.0.0.1:8000/mcp`).

    If you want to verify the env file exists first:

    - `Test-Path src/devui/fabric_de_agent/.env`

1. Start DevUI:

    - `devui ./src/devui --port 8080`

## Tests and lint

- Run tests: `pytest`
- Run lint: `ruff check .`

## Code-health checks (optional)

- Approximate dead-code detection: `python -m vulture src --min-confidence 80`
- Coverage: `python -m pytest --cov=fabric_de_mcp --cov-report=term-missing`

## Architecture map (where to make changes)

- MCP server + CLI: `src/fabric_de_mcp/server.py`
  - Public tool wrappers live here.
  - The console script points at `fabric_de_mcp.server:cli` (see `pyproject.toml`).
- Fabric REST calls: `src/fabric_de_mcp/fabric/api.py`
  - Build outbound requests using `requests`.
  - Use `build_session(retries, backoff)` (Retry handles 408/409/429/5xx).
  - For pipeline creation, `encode_definition()` base64-inlines JSON definition files.
- Auth: `src/fabric_de_mcp/fabric/auth.py`
  - Uses `DefaultAzureCredential` to get a bearer token.
  - Tool wrappers allow a `token` override.
- Errors: `src/fabric_de_mcp/fabric/errors.py` (`FabricApiError`).
- Configuration: `src/fabric_de_mcp/config.py`
  - `FABRIC_BASE_URL` (default `https://api.fabric.microsoft.com/v1`)
  - `FABRIC_SCOPE` (default `https://api.fabric.microsoft.com/.default`)

## DevUI agent structure (public convention)

DevUI directory discovery expects each agent directory to export `agent` from `__init__.py`.

- Agent folder: `src/devui/fabric_de_agent/`

  - `__init__.py` exports: `agent`
  - `agent.py` contains the implementation

## Conventions (repo-specific)

- Prefer editing production code under `src/` (src-layout packaging).
- Treat MCP tool names + parameters as **public API**.
  - Avoid renaming tools or breaking parameters.
  - If you must change a parameter, prefer adding a new optional parameter instead of modifying/removing one.
- HTTP behavior:
  - Return `resp.json()` for success.
  - Raise `FabricApiError(status_code, resp.text)` on non-2xx/202.

## Adding a new MCP tool (pattern)

1. Implement the REST call in `src/fabric_de_mcp/fabric/api.py` (use `build_session`).
2. Add a thin `@app.tool()` wrapper in `src/fabric_de_mcp/server.py` that:
   - Accepts `token: Optional[str] = None`
   - Calls `token or get_token()`
   - Delegates to the `fabric.api` function
3. If the tool needs sample payloads, add them under `assets/` (see `assets/pipelines/`).

## Security

- Never commit secrets (bearer tokens, keys). Don’t log tokens or include them in exceptions.
- Prefer `DefaultAzureCredential` for auth; keep local secrets in a git-ignored `.env`.

## VS Code Copilot customization files

- Put agent/prompt/instruction files under `.github/agents/`, `.github/prompts/`, `.github/instructions/`.
