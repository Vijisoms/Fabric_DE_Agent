# MCP internals (tools + Fabric REST)

This document breaks down how the MCP server operates.

## MCP server state (conceptual)

The server is typically run in **Streamable HTTP** mode and serves the MCP endpoint at `/mcp`.

```mermaid
stateDiagram-v2
  [*] --> Starting
  Starting: Process starts
  Starting --> Listening: FastMCP app.run(streamable-http)
  Listening --> HandlingRequest: HTTP request received
  HandlingRequest --> ResolvingAuth: token override OR get_token()
  ResolvingAuth --> CallingFabric: requests.Session.request
  CallingFabric --> Responding: success JSON or FabricApiError
  Responding --> Listening
```

## Tool call flow (from code)

Tool functions live in `src/fabric_de_mcp/server.py` and follow this pattern:

- Accept arguments for operation (workspace/item ids, names, etc.)
- Accept optional `token` override
- If `token` is not provided, call `get_token()`
- Delegate to `fabric_de_mcp.fabric.api` for HTTP calls

```mermaid
flowchart LR
  classDef code fill:#ecfeff,stroke:#0891b2,stroke-width:1px,color:#111827;
  classDef api fill:#eef2ff,stroke:#4f46e5,stroke-width:1px,color:#111827;
  classDef err fill:#fee2e2,stroke:#b91c1c,stroke-width:1px,color:#111827;

  Tool["@app.tool()<br/>create_item / list_items / ..."]:::code
  Auth["fabric/auth.py<br/>get_token()"]:::code
  Api["fabric/api.py<br/>_request()"]:::code
  Ok["resp.json() or {}"]:::api
  Err["FabricApiError(status, body)"]:::err

  Tool -->|"token empty"| Auth
  Tool --> Api
  Api -->|"2xx/202"| Ok
  Api -->|"non-ok"| Err
```

## Fabric REST endpoints used

These map directly to functions in `src/fabric_de_mcp/fabric/api.py`:

- Workspaces
  - `GET /v1/workspaces`
- Items
  - `POST /v1/workspaces/{workspaceId}/items`
  - `GET /v1/workspaces/{workspaceId}/items`
  - `GET /v1/workspaces/{workspaceId}/items/{itemId}`
  - `PATCH /v1/workspaces/{workspaceId}/items/{itemId}`
  - `POST /v1/workspaces/{workspaceId}/items/{itemId}/getDefinition`
  - `POST /v1/workspaces/{workspaceId}/items/{itemId}/updateDefinition`
- Lakehouse
  - `GET /v1/workspaces/{workspaceId}/lakehouses/{lakehouseId}`
  - `GET /v1/workspaces/{workspaceId}/lakehouses/{lakehouseId}/tables`
- Pipeline jobs
  - `POST /v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances?jobType=Pipeline`
  - `GET /v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances/{jobInstanceId}`

## Retry behavior

HTTP retries are configured in `build_session(retries, backoff)` using `requests.adapters.Retry`:

- Retries on: `408, 409, 429, 500, 502, 503, 504`
- Methods: `HEAD, GET, OPTIONS, POST, PATCH`
