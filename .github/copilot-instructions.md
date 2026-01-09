# Repo-wide Copilot instructions

- Prefer editing code under `src/` (src-layout packaging).
- Keep MCP tools stable: avoid breaking tool names or parameter schemas.
- Never commit secrets (bearer tokens, keys). Use DefaultAzureCredential and `.env` locally.
- For Fabric operations, prefer `fabric_de_mcp.fabric.api` helpers rather than duplicating HTTP logic.
- For new prompts/agents, place files in `.github/prompts` and `.github/agents`.
