from __future__ import annotations

import os
import textwrap
from pathlib import Path

from typing import TYPE_CHECKING

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.azure import AzureAIAgentClient, AzureOpenAIChatClient

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

try:
    from azure.identity.aio import DefaultAzureCredential
except ImportError:  # pragma: no cover
    DefaultAzureCredential = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from agent_framework._mcp import MCPTool
else:
    try:
        from agent_framework._mcp import MCPTool
    except ImportError:  # pragma: no cover
        MCPTool = MCPStreamableHTTPTool  # type: ignore[misc,assignment]


def _load_env_files() -> None:
    if load_dotenv is None:
        return

    agent_dir = Path(__file__).resolve().parent

    # Keep DevUI config isolated: only load an env file colocated with the agent.
    env_path = agent_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


def _foundry_project_endpoint() -> str | None:
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT") or os.getenv(
        "AZURE_EXISTING_AIPROJECT_ENDPOINT"
    )
    if endpoint:
        return endpoint

    # Compatibility: users sometimes paste a Foundry project endpoint into AZURE_OPENAI_ENDPOINT.
    fallback = os.getenv("AZURE_OPENAI_ENDPOINT")
    if fallback and "services.ai.azure.com" in fallback:
        return fallback
    return None


def _foundry_model_deployment_name() -> str | None:
    name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    if name:
        return name

    return os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")


def _build_chat_client():
    _load_env_files()
    project_endpoint = _foundry_project_endpoint()
    if project_endpoint:
        if DefaultAzureCredential is None:
            raise SystemExit(
                "azure-identity is required for Azure AI Foundry auth. "
                "Install with: pip install azure-identity"
            )
        credential = DefaultAzureCredential()
        return AzureAIAgentClient(
            project_endpoint=project_endpoint,
            model_deployment_name=_foundry_model_deployment_name(),
            credential=credential,
            should_cleanup_agent=False,
        )

    return AzureOpenAIChatClient()


chat_client = _build_chat_client()

# NOTE: For DevUI, don't use `async with` around MCP tools. DevUI will manage
# the tool lifecycle and connections are established lazily on first use.
tools: list[MCPTool] = [
    MCPStreamableHTTPTool(
        name="fabric_de_mcp",
        url=(os.getenv("FABRIC_DE_MCP_SERVER_URL") or "http://127.0.0.1:8000/mcp").strip(),
        load_prompts=False,
    )
]
if fabric_mcp_url := os.getenv("FABRIC_MCP_URL"):
    tools.append(
        MCPStreamableHTTPTool(
            name="Microsoft Fabric MCP",
            url=fabric_mcp_url.strip(),
        )
    )

# tools.append(
#     MCPStreamableHTTPTool(
#         name="fabric_mcp",
#         url=(os.getenv("FABRIC_MCP_URL") or "http://127.0.0.1:5001").strip(),
#         load_prompts=False,
#     )
# )



INSTRUCTIONS = textwrap.dedent(
    """\
    You are a Microsoft Fabric Data Engineering assistant.
    You can use the available MCP tools (fabric_de_mcp) to list workspaces,
    create items (Lakehouse, DataPipeline), and inspect/update items.

    If a second MCP server is configured via FABRIC_MCP_URL, you can also
    use the available MCP tools (fabric_mcp).

    Definition-first rule (STRICT): 
    - If fabric_mcp is available and the user request requires a JSON definition/payload (for example: creating/updating a DataPipeline,
      Notebook, SparkJobDefinition, etc.), you MUST call fabric_mcp tools first to generate and/or validate the required definition.
    - Only after fabric_mcp returns a usable definition should you call fabric_de_mcp tools that create/update resources.
    - This rule applies specifically to these fabric_de_mcp operations:
      - fabric_de_mcp.create_pipeline
      - fabric_de_mcp.create_item
      - fabric_de_mcp.update_item
    - Exception: you may skip fabric_mcp only if the user already provided an explicit, complete definition (or a server-local definition_path)
      AND the user explicitly told you to proceed.
    - Use the Fabric MCP tools to generate/validate definitions by referring to resources and definition in this MCP server.

    Pipeline creation workflow (REQUIRED when fabric_mcp is available):
    - Step 1 (definition): Call a fabric_mcp tool to generate or validate a *Fabric DataPipeline definition* using the resources and definition available in the tool.
      - Ensure the copy activity uses valid linkedService settings and make sure Table action in sink is required.
      - The output must be either:
        - a JSON definition object you can pass as the `definition` parameter, OR
        - a file path you can pass as `definition_path` (only if that file exists on the MCP server host).
    - Step 2 (create): Call fabric_de_mcp.create_pipeline (preferred) or fabric_de_mcp.create_item with:
      - workspace_id
      - name
      - and the `definition`/`definition_path` obtained from Step 1.      
    - Do not call fabric_de_mcp.create_pipeline/create_item until Step 1 has produced a usable definition, unless the user explicitly provides a definition/definition_path and tells you to proceed.
    - when definition is given, create_pipeline / create_item tool will wrap raw pipeline JSON into a multi part definition with pipeline-content.json and .platform will be done in the create_pipeline tool
    - If fabric_mcp is NOT configured/available, ask the user for a valid pipeline definition JSON or a definition file path.
    Tool use rules:
    - Prefer MCP tool calls over guessing.
    - Do not claim an item was created/updated unless the MCP tool call succeeded.
    - If a tool call fails, explain what failed and ask for the missing inputs.

    Auth note:
    - The MCP server supports an optional 'token' parameter, but when running
      locally it typically uses DefaultAzureCredential automatically.
    """
).strip()

agent = ChatAgent(
    name="fabric_de_agent",
    chat_client=chat_client,
    tools=tools,
    instructions=INSTRUCTIONS,
)
