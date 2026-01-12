# Folder structure

This repo uses a Python `src/` layout.

## Key locations

- `src/fabric_de_mcp/`: production code (MCP server + Fabric helpers)
- `src/fabric_de_mcp/requirements.txt`: MCP runtime dependencies
- `src/devui/`: local DevUI agent(s) for testing the MCP server
- `src/devui/requirements.txt`: DevUI/Agent Framework dependencies
- `requirements-dev.txt`: repo dev tools (tests, lint, code-health)
- `.github/agents/`: VS Code custom agents (`*.agent.md`)
- `.github/prompts/`: VS Code prompt files (`*.prompt.md`)
- `.github/instructions/`: VS Code instruction files (`*.instructions.md`)
- `assets/`: non-code assets like sample pipeline definitions
- `tests/`: tests

