 ---
agent: agent
---

You are helping a developer switch between a local MCP server and a deployed Container App MCP server for the DevUI.

Use these rules and do the following guidelines when running these workflows:
- Use the DevUI env file at src/devui/fabric_de_agent/.env.
- Use the key FABRIC_DE_MCP_SERVER_URL (not MCP_SERVER_URL).
- For local MCP, the URL should be http://127.0.0.1:8000/mcp.


Use these commands where applicable:
- Local MCP: python -m fabric_de_mcp (run from repo root).
- DevUI: devui ./src/devui --port 8080

Success criteria: After following either section, DevUI connects to the intended MCP endpoint.
Start DevUI after updating the env file to verify the connection.


