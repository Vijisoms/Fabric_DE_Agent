# DevUI + Agent Framework dataflow

This document explains the runtime dataflow when using DevUI to test the MCP server.

## Directory discovery structure

DevUI directory discovery expects each agent directory to export `agent` from its `__init__.py`.

This repo follows the sample structure:

```text
src/devui/
  fabric_de_agent/
    __init__.py      # exports: agent
    agent.py         # agent implementation
    .env.example
```

## End-to-end sequence (DevUI → MCP → Fabric)

```mermaid
sequenceDiagram
  autonumber
  participant UI as DevUI (web)
  participant Agent as ChatAgent
  participant Tool as MCP Tool<br/>(HTTP / WebSocket / Stdio)
  participant MCP as MCP Server (FastMCP /mcp)
  participant Auth as get_token (DefaultAzureCredential)
  participant Fabric as Fabric REST API

  UI->>Agent: User message
  loop For each required tool call
    Agent->>Tool: Decide tool call
    Tool->>MCP: HTTP request (Streamable HTTP)
    MCP->>Auth: token or get_token()
    Auth-->>MCP: Bearer token
    MCP->>Fabric: HTTP request with Authorization: Bearer
    Fabric-->>MCP: JSON response
    MCP-->>Tool: Tool result
    Tool-->>Agent: Tool result
  end
  Agent-->>UI: Assistant response
```

## Request/response payload shape (conceptual)

At runtime, you should think of the payloads in three layers:

1. **DevUI conversation request** (OpenAI-compatible API)
2. **Tool invocation** (Agent Framework → MCP tool)
3. **Fabric REST call** (`requests` → `https://api.fabric.microsoft.com/v1/...`)

```mermaid
flowchart TD
  classDef box fill:#f7f7f7,stroke:#6b7280,stroke-width:1px,color:#111827;
  classDef api fill:#eef2ff,stroke:#4f46e5,stroke-width:1px,color:#111827;
  classDef http fill:#ecfeff,stroke:#0891b2,stroke-width:1px,color:#111827;

  UI["DevUI Request<br/>input: text + files"]:::api
  TOOL["MCP tool call<br/>name + args"]:::http
  FAB["Fabric REST request<br/>method + url + json"]:::http

  UI --> TOOL --> FAB
```

## Local vs Azure

- **Local**: `FABRIC_DE_MCP_SERVER_URL` can be `http://127.0.0.1:8000/mcp`.
- **Azure Container App**: `FABRIC_DE_MCP_SERVER_URL` should be `https://<containerapp-fqdn>/mcp`.
