---
agent: agent
---

You are helping a developer switch between a local MCP server and a deployed Container App MCP server for the DevUI.


Requirements:
- Use src/devui/fabric_de_agent/.env for configuration.
- Set FABRIC_DE_MCP_SERVER_URL to exactly one active endpoint at a time.
- Comment out the unused endpoint line.
- For ContainerMCP, the URL should be "https://azcaorefwypsrdv4i.wonderfulbay-bb5587e7.eastus.azurecontainerapps.io/mcp"
- Do not include real hostnames, secrets, or subscription/tenant IDs.

Use these commands where applicable:
- DevUI: devui ./src/devui --port 8080

Success criteria: After following either section, DevUI connects to the intended MCP endpoint.
Start DevUI after updating the env file to verify the connection.

