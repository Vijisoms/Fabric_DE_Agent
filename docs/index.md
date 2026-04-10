# Documentation

This folder contains the canonical documentation for this repository (beyond the root `README.md`).

## Start here

- [Architecture overview](architecture.md)
- [DevUI + Agent Framework dataflow](devui-dataflow.md)
- [MCP internals (tools + REST calls)](mcp-internals.md)
- [Authentication & authorization](auth.md)
- [Fabric-de-agent-new (Foundry agent)](fabric-de-agent-new.md)

## Conventions

- Diagrams are authored in Mermaid.
- Diagrams are validated against the current code paths in:
  - `src/fabric_de_mcp/server.py`
  - `src/fabric_de_mcp/fabric/api.py`
  - `src/fabric_de_mcp/fabric/auth.py`
  - `src/devui/fabric_de_agent/agent.py`
  - `infra/main.bicep`
