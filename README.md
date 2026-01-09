# Fabric_DE_MCP

Small Python utilities + an MCP server for Microsoft Fabric Data Engineering tasks (create Lakehouse and Pipeline items).

Production code lives under `src/` (Python src-layout).

## Quick start

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Optionally install as an editable package:

```bash
pip install -e .
```

## Run the MCP server locally

```bash
python -m fabric_de_mcp
```

## Security

- Do **not** commit bearer tokens, keys, or connection strings.
- Prefer interactive auth (Azure CLI / managed identity) when possible.
- Local secrets belong in `.env` (ignored by git) or a secure secret store.

## Repo contents

- `src/fabric_de_mcp/`: MCP server + Fabric REST helpers.
- `.github/agents`, `.github/prompts`, `.github/instructions`: VS Code Copilot customization assets.
- `assets/`: Sample assets (pipeline definitions, etc.).
