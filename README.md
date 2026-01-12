# Fabric DE MCP

An MCP (Model Context Protocol) server for automating Microsoft Fabric Data Engineering tasks.

This repository provides a small, focused set of **MCP tools** that wrap the Microsoft Fabric REST API so an MCP-capable client (agent, app, IDE integration, etc.) can create Fabric items programmatically.

## What this repo is for

- **Expose Fabric automation as MCP tools** over the `streamable-http` transport.
- **Handle auth and retries** in one place.
- Provide a clean starting point to add more Fabric Data Engineering operations.

Today, the server supports creating:

- **Lakehouse** items
- **Data Pipeline** items (optionally with an inline base64 definition)

## How it works (high level)

- The MCP server is implemented with `mcp.server.fastmcp.FastMCP`.
- Requests to Microsoft Fabric go to the REST endpoint (default: `https://api.fabric.microsoft.com/v1`).
- Authentication uses `azure.identity.DefaultAzureCredential` (Azure CLI, Managed Identity, service principal env vars, etc.).
- The tool functions accept an optional `token` override if you want to supply a bearer token directly.

## Tools exposed

The server registers these tools:

### `list_workspaces`

Lists workspaces in the current Fabric tenant.

Parameters:

- `token` (string, optional) – bearer token override
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `create_item`

Creates a Fabric item in a workspace (generic). Use this for any supported `item_type`.

Parameters:

- `workspace_id` (string, required)
- `name` (string, required)
- `item_type` (string, required) – e.g. `Lakehouse`, `Notebook`, `SparkJobDefinition`, `DataPipeline`
- `token` (string, optional) – bearer token override
- `description` (string, optional)
- `definition_path` (string, optional) – path to a JSON definition file; the server base64-inlines the file contents
- `definition` (object/dict, optional) – pre-built Fabric definition payload (alternative to `definition_path`)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `create_lakehouse`

Creates a Lakehouse item in a Fabric workspace.

Parameters:

- `workspace_id` (string, required)
- `name` (string, required)
- `token` (string, optional) – bearer token override
- `description` (string, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `create_pipeline`

Creates a Data Pipeline item in a Fabric workspace.

Parameters:

- `workspace_id` (string, required)
- `name` (string, required)
- `token` (string, optional) – bearer token override
- `description` (string, optional)
- `definition_path` (string, optional) – path to a JSON pipeline definition file; the server base64-inlines the file contents
- `definition` (object/dict, optional) – pre-built Fabric definition payload (alternative to `definition_path`)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

Sample pipeline definition files live under `assets/pipelines/`.

### `list_items`

Lists items in a workspace.

Parameters:

- `workspace_id` (string, required)
- `token` (string, optional)
- `continuation_url` (string, optional) – use when the service returns a continuation URI
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `get_item`

Gets item properties by workspace and item id.

Parameters:

- `workspace_id` (string, required)
- `item_id` (string, required)
- `token` (string, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `update_item`

Updates item metadata (display name / description).

Parameters:

- `workspace_id` (string, required)
- `item_id` (string, required)
- `token` (string, optional)
- `name` (string, optional)
- `description` (string, optional)
- `item_type` (string, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `get_item_definition`

Gets the definition for a Fabric item (base64 parts).

Parameters:

- `workspace_id` (string, required)
- `item_id` (string, required)
- `token` (string, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `update_item_definition`

Updates the definition for a Fabric item.

Parameters:

- `workspace_id` (string, required)
- `item_id` (string, required)
- `token` (string, optional)
- `name` (string, optional)
- `item_type` (string, optional)
- `definition_path` (string, optional)
- `definition` (object/dict, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `get_lakehouse`

Gets lakehouse properties.

Parameters:

- `workspace_id` (string, required)
- `lakehouse_id` (string, required)
- `token` (string, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `list_lakehouse_tables`

Lists tables in a lakehouse.

Parameters:

- `workspace_id` (string, required)
- `lakehouse_id` (string, required)
- `token` (string, optional)
- `max_results` (int, optional)
- `continuation_url` (string, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `run_pipeline_job_instance`

Runs an on-demand pipeline job instance.

Parameters:

- `workspace_id` (string, required)
- `item_id` (string, required)
- `token` (string, optional)
- `execution_data` (object/dict, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

### `get_pipeline_job_instance`

Gets status for a pipeline job instance.

Parameters:

- `workspace_id` (string, required)
- `item_id` (string, required)
- `job_instance_id` (string, required)
- `token` (string, optional)
- `timeout` (float, default `30`)
- `retries` (int, default `3`)
- `backoff` (float, default `0.5`)

## Non-goals

- This server intentionally does **not** expose Fabric delete REST APIs.

## Requirements

- Python `>= 3.10`

## Install

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r src/fabric_de_mcp/requirements.txt
```

Editable install (recommended for development):

```bash
python -m pip install -e .
```

Developer tools (tests + lint):

```bash
python -m pip install -r requirements-dev.txt
```

## Run locally

Run as a module:

```bash
python -m fabric_de_mcp
```

## Run the DevUI (local)

This repo supports a local web UI using **Microsoft Agent Framework DevUI**.

DevUI discovers agents from [src/devui/fabric_de_agent](src/devui/fabric_de_agent/__init__.py).
The agent connects to this repo's MCP server via Streamable HTTP, so you can chat and invoke the MCP tools.

### Windows (PowerShell)

1. Create + activate a virtual environment:
   - `python -m venv .venv`
   - `./.venv/Scripts/Activate.ps1`

2. Install DevUI / Agent Framework dependencies (pre-release packages):
   - `python -m pip install --pre -r src/devui/requirements.txt`


3. Configure environment variables (recommended):
   - Copy `src/devui/fabric_de_agent/.env.example` to `src/devui/fabric_de_agent/.env` and fill in either:
     - **Azure AI Foundry Project** (`AZURE_AI_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`), or
     - **Azure OpenAI** (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`).
   - Set `MCP_SERVER_URL` to the MCP endpoint you want DevUI to call:
     - **Local MCP** (this repo running locally): `http://127.0.0.1:8000/mcp`
     - **Deployed MCP (Azure Container Apps)**: `https://<containerapp-fqdn>/mcp`

   Notes:
   - The `/mcp` path matters.
   - For Azure Container Apps, use the app's public ingress FQDN.
   - Do not commit real hostnames/endpoints; keep them in your local `.env`.

4. Start the MCP server (skip this if you're using the deployed Azure Container App MCP):
   - `python -m fabric_de_mcp`

5. Start DevUI:
   - `devui ./src/devui --port 8080`

DevUI opens a browser (default: `http://localhost:8080`).

### Troubleshooting

- **Port already in use**: pick a different port:
  - `devui ./src/devui --port 8081`
- **Stop DevUI**: focus the terminal and press `Ctrl+C`.

Or via the console script:

```bash
fab-de-mcp --transport streamable-http
```

More notes: see `docs/run-local.md`.

## Using a deployed MCP (Azure Container Apps)

You can run DevUI locally while pointing it at a remotely deployed MCP server.

### Deploy with Azure Developer CLI (`azd`)

This repo is set up for `azd` (see `azure.yaml` and `infra/`).

1. Install prerequisites (one time):
   - Azure CLI (`az`) and Azure Developer CLI (`azd`)
2. Authenticate:
   - `az login`
3. Provision + deploy:
   - `azd up`

After `azd up`, get the Container App FQDN from the deployment outputs:

- `azd env get-values | findstr CONTAINER_APP_FQDN`

The MCP endpoint is:

- `https://<CONTAINER_APP_FQDN>/mcp`

### Point DevUI at the deployed MCP

1. Copy `src/devui/fabric_de_agent/.env.example` to `src/devui/fabric_de_agent/.env`.
2. Set `MCP_SERVER_URL` to the deployed endpoint:

   - `MCP_SERVER_URL=https://<containerapp-fqdn>/mcp`

3. Start DevUI:

   - `devui ./src/devui --port 8080`

When using the deployed MCP server, Fabric credentials are handled by the MCP server's runtime identity
(for example Managed Identity in Azure) rather than your local DevUI process.

## Authentication

By default, the server acquires tokens using `DefaultAzureCredential`.

Typical local setup options:

- **Azure CLI**: sign in once with `az login` (then run the server)
- **Service principal**: set environment variables supported by `DefaultAzureCredential`
- **Managed identity**: when running in an Azure-hosted environment

If you already have a bearer token, you can pass it directly via the `token` parameter for either tool.

## Configuration

Environment variables (optional):

- `FABRIC_BASE_URL` (default: `https://api.fabric.microsoft.com/v1`)
- `FABRIC_SCOPE` (default: `https://api.fabric.microsoft.com/.default`)

### Local `.env` files

- MCP server: copy `src/fabric_de_mcp/.env.example` to `src/fabric_de_mcp/.env`
- DevUI agent: copy `src/devui/fabric_de_agent/.env.example` to `src/devui/fabric_de_agent/.env`

Both are loaded automatically at runtime (when `python-dotenv` is installed).

## Repo structure

- `src/fabric_de_mcp/`: production code (MCP server + Fabric REST helpers)
- `tests/`: tests
- `assets/`: sample assets (pipeline definitions, etc.)
- `docs/`: short developer docs
- `.github/agents`, `.github/prompts`, `.github/instructions`: VS Code Copilot customization assets

More detail: see `docs/folder-structure.md`.

## Documentation

- Start here: [docs/index.md](docs/index.md)

## Development

Run tests:

```bash
pytest
```

Run lint:

```bash
ruff check .

```

Optional code-health checks:

```bash
# Approximate dead-code detection (best-effort; may need allowlists for false positives)
python -m vulture src --min-confidence 80

# Test coverage for the MCP package
python -m pytest --cov=fabric_de_mcp --cov-report=term-missing
```

## Security notes

- Do **not** commit bearer tokens, keys, or connection strings.
- Prefer `DefaultAzureCredential` for auth rather than hard-coding secrets.
- Keep local secrets in `.env` (git-ignored) or a secure secret store.

## Roadmap ideas

- Add additional Fabric Data Engineering operations (list items, delete items, update item definitions, wait/poll for long-running operations).
- Add richer error handling (surface correlation IDs / request IDs when available).
- Add examples for common MCP clients and integration patterns.
