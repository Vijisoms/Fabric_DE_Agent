# Architecture

This repo has two distinct entry points:

1. **MCP Server (production purpose)**: `fabric_de_mcp` exposes MCP tools over Streamable HTTP.
2. **DevUI + Agent Framework (local testing UI)**: DevUI hosts a chat UI and an OpenAI-compatible API that talks to the MCP server via `MCPStreamableHTTPTool`.

## System context (DevUI → MCP → Fabric)

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "ui-sans-serif, system-ui", "fontSize": "14px"}}}%%
flowchart LR
  %% Mermaid styling best practice: define reusable classes.
  classDef ui fill:#f7f7f7,stroke:#6b7280,stroke-width:1px,color:#111827;
  classDef svc fill:#eef2ff,stroke:#4f46e5,stroke-width:1px,color:#111827;
  classDef data fill:#ecfeff,stroke:#0891b2,stroke-width:1px,color:#111827;
  classDef azure fill:#fef3c7,stroke:#d97706,stroke-width:1px,color:#111827;

  U["Developer<br/>Browser"]:::ui
  D["DevUI<br/>(agent-framework-devui)"]:::svc
  A["ChatAgent<br/>(agent_framework)"]:::svc
  T["MCPStreamableHTTPTool<br/>(Streamable HTTP client)"]:::svc

  ACA["Azure Container App<br/>fabdemcp"]:::azure
  MCP["FastMCP server<br/>/mcp"]:::svc
  FAB["Microsoft Fabric REST API<br/>api.fabric.microsoft.com/v1"]:::azure

  U -->|"chat"| D
  D -->|"invokes"| A
  A -->|"tool call"| T
  T -->|"HTTP"| ACA
  ACA --> MCP
  MCP -->|"HTTP"| FAB

  subgraph Repo["This repo"]
    direction TB
    SRV["src/fabric_de_mcp/server.py"]:::data
    DEV["src/devui/fabric_de_agent/agent.py"]:::data
  end

  MCP --- SRV
  A --- DEV
```

## Azure Container Apps deployment (high-level)

The infra template provisions:

- **ACR** for container images
- **User-assigned managed identity** (UAMI)
- **Container App Environment** + **Container App** with ingress on port `8000`

```mermaid
flowchart TB
  classDef azure fill:#fef3c7,stroke:#d97706,stroke-width:1px,color:#111827;
  classDef svc fill:#eef2ff,stroke:#4f46e5,stroke-width:1px,color:#111827;
  classDef data fill:#ecfeff,stroke:#0891b2,stroke-width:1px,color:#111827;

  ACR["Azure Container Registry (ACR)"]:::azure
  UAMI["User-assigned Managed Identity"]:::azure
  CAE["Container Apps Environment"]:::azure
  CA["Container App<br/>Ingress: external<br/>Target port: 8000"]:::azure
  IMG["Container image<br/>fab-de-mcp"]:::data
  ENV["Env vars<br/>FASTMCP_HOST=0.0.0.0<br/>FASTMCP_PORT=8000"]:::data

  IMG --> ACR
  CA -->|"pull image via AcrPull"| ACR
  CA -->|"uses"| UAMI
  CA --> CAE
  CA --- ENV
```

## Key modules

- `src/fabric_de_mcp/server.py`
  - MCP tool registration (`@app.tool()`)
  - Tool wrappers accept an optional `token` override
  - Runs Streamable HTTP transport
- `src/fabric_de_mcp/fabric/auth.py`
  - `DefaultAzureCredential()` token acquisition
- `src/fabric_de_mcp/fabric/api.py`
  - Fabric REST calls, retries, and request/response handling
- `src/devui/fabric_de_agent/agent.py`
  - DevUI-discoverable `agent = ChatAgent(...)` that connects to the MCP server
