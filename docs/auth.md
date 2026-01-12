# Authentication & authorization

This repo uses **Azure Identity** to obtain bearer tokens for Fabric.

## Authentication flow

`src/fabric_de_mcp/fabric/auth.py` uses `DefaultAzureCredential()`.

```mermaid
sequenceDiagram
  autonumber
  participant Client as MCP Tool Wrapper
  participant Cred as DefaultAzureCredential
  participant AAD as Microsoft Entra ID

  Client->>Cred: get_token(scope)
  Note over Cred: Chooses one available credential source
  Note over Cred: (Azure CLI, Managed Identity, etc.)
  Cred->>AAD: Token request for FABRIC_SCOPE
  AAD-->>Cred: Access token (Bearer)
  Cred-->>Client: token
```

## Authorization (what the token can do)

Authorization is ultimately enforced by **Fabric**.

```mermaid
flowchart LR
  classDef actor fill:#f7f7f7,stroke:#6b7280,stroke-width:1px,color:#111827;
  classDef auth fill:#eef2ff,stroke:#4f46e5,stroke-width:1px,color:#111827;
  classDef policy fill:#ecfeff,stroke:#0891b2,stroke-width:1px,color:#111827;
  classDef deny fill:#fee2e2,stroke:#b91c1c,stroke-width:1px,color:#111827;
  classDef allow fill:#dcfce7,stroke:#16a34a,stroke-width:1px,color:#111827;

  ID["Identity<br/>(UAMI / user / SP)"]:::actor
  TOK["Bearer token<br/>FABRIC_SCOPE"]:::auth
  FAB["Fabric REST API"]:::auth
  RBAC["Fabric permissions<br/>(workspace/item access)"]:::policy
  OK["200/202"]:::allow
  NO["403/401"]:::deny

  ID --> TOK --> FAB
  FAB --> RBAC
  RBAC -->|"allowed"| OK
  RBAC -->|"denied"| NO
```

## Important notes

- The MCP tool wrappers accept an optional `token` parameter. If provided, the server will use it.
- If `token` is omitted, the server will acquire one using `DefaultAzureCredential`.
- In Azure Container Apps, `DefaultAzureCredential` can use Managed Identity when configured.
