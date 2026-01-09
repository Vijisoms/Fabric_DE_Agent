# Fabric_DE_Agent

Small Python utilities + an MCP server for Microsoft Fabric Data Engineering tasks (create Lakehouse and Pipeline items).

## Quick start

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Security

- Do **not** commit bearer tokens, keys, or connection strings.
- Prefer interactive auth (Azure CLI / managed identity) when possible.
- Local secrets belong in `.env` (ignored by git) or a secure secret store.

## Repo contents

- `fab_de_mcp.py`: Streamable MCP server exposing Fabric operations.
- `create_pipeline.py`: CLI to create a Fabric pipeline item.
- `create_lakehouse.py`: CLI to create a Fabric lakehouse item.
- `Approved/`: Sample/approved pipeline definitions.
