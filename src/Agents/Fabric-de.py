"""Azure AI Foundry Agent + MCP tool registration.

This script updates/creates an agent version that includes your MCP server as a tool,
then sends a simple message to the agent using the Responses API.

Prereqs:
  - `pip install -r requirements-agent-ui.txt`
  - Set env vars:
      - AZURE_AI_PROJECT_ENDPOINT (or edit PROJECT_ENDPOINT below)
      - AZURE_AI_MODEL_DEPLOYMENT_NAME
      - MCP_SERVER_URL (after deployment, e.g. https://<fqdn>/mcp)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / "config" / ".env")
load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT") or os.getenv(
    "AZURE_EXISTING_AIPROJECT_ENDPOINT"
)

AGENT_NAME = (
    os.getenv("AGENT_NAME") or os.getenv("AZURE_EXISTING_AGENT_ID") or "Fabric-DE-Agent"
)
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

# Optional (recommended for authenticated MCP servers): store auth + endpoint details
# in a Foundry Project Connection and reference it here.
MCP_PROJECT_CONNECTION_ID = os.getenv("MCP_PROJECT_CONNECTION_ID") or os.getenv(
    "MCP_PROJECT_CONNECTION_NAME"
)

# Optional: additional headers to send to the MCP server (JSON object)
# Example: {"X-Api-Key": "..."}
MCP_HEADERS_JSON = os.getenv("MCP_HEADERS_JSON")

# Optional: restrict which tools are callable from the MCP server.
# Example: "create_lakehouse,create_pipeline"
MCP_ALLOWED_TOOLS = os.getenv("MCP_ALLOWED_TOOLS")

# Optional: approval policy for MCP tool calls.
# Supported by Foundry docs: "always" (default) or "never".
MCP_REQUIRE_APPROVAL = (os.getenv("MCP_REQUIRE_APPROVAL") or "never").strip()

if not PROJECT_ENDPOINT:
    raise SystemExit(
        "Missing AZURE_AI_PROJECT_ENDPOINT (example: "
        "https://<resource>.services.ai.azure.com/api/projects/<project>)"
    )
if not MODEL_DEPLOYMENT:
    raise SystemExit("Missing AZURE_AI_MODEL_DEPLOYMENT_NAME")
if not MCP_SERVER_URL:
    raise SystemExit("Missing MCP_SERVER_URL (example: https://<fqdn>/mcp)")

headers: dict[str, str] | None = None
if MCP_HEADERS_JSON:
    try:
        parsed = json.loads(MCP_HEADERS_JSON)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid MCP_HEADERS_JSON (must be JSON object): {e}") from e
    if not isinstance(parsed, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in parsed.items()
    ):
        raise SystemExit("MCP_HEADERS_JSON must be a JSON object of string->string")
    headers = parsed

allowed_tools: list[str] | None = None
if MCP_ALLOWED_TOOLS:
    allowed_tools = [t.strip() for t in MCP_ALLOWED_TOOLS.split(",") if t.strip()]

require_approval: str | dict
if MCP_REQUIRE_APPROVAL.startswith("{"):
    try:
        parsed_approval = json.loads(MCP_REQUIRE_APPROVAL)
    except json.JSONDecodeError as e:
        raise SystemExit(
            'Invalid MCP_REQUIRE_APPROVAL JSON (expected e.g. {"never":["tool1"]})'
        ) from e
    if not isinstance(parsed_approval, dict):
        raise SystemExit("MCP_REQUIRE_APPROVAL JSON must be an object")
    require_approval = parsed_approval
else:
    if MCP_REQUIRE_APPROVAL not in {"always", "never"}:
        raise SystemExit('MCP_REQUIRE_APPROVAL must be "always", "never", or a JSON object')
    require_approval = MCP_REQUIRE_APPROVAL

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # Create/update an agent version that includes the MCP tool
    mcp_tool = MCPTool(
        server_label="fabdemcp",
        server_url=MCP_SERVER_URL,
        require_approval=require_approval,
        headers=headers,
        allowed_tools=allowed_tools,
        project_connection_id=MCP_PROJECT_CONNECTION_ID,
    )

    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT,
            instructions=(
                "You are a helpful Fabric Data Engineering assistant. "
                "Use the fabdemcp MCP tools when you need to create lakehouses or pipelines."
            ),
            tools=[mcp_tool],
        ),
        description="Fabric DE agent with MCP tool",
    )

    print(f"Agent ready: name={agent.name}, version={getattr(agent, 'version', 'unknown')}")

    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input="Tell me what you can help with.",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Response output: {response.output_text}")



