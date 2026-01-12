from __future__ import annotations

import os
from pathlib import Path

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

_DEFAULT_MCP_URL = "http://127.0.0.1:8000/mcp"


def _mcp_url() -> str:
    return os.getenv("MCP_SERVER_URL") or _DEFAULT_MCP_URL


def _load_env_files() -> None:
    if load_dotenv is None:
        return

    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / "config" / ".env",
        repo_root / "entities" / ".env",
        repo_root / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path, override=False)


def _foundry_project_endpoint() -> str | None:
    # Primary (documented) env var for Foundry projects.
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
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

    # Compatibility: users sometimes set chat deployment name thinking it's the same setting.
    return os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")


def _build_chat_client():
    # Load local env files if present (git-ignored).
    _load_env_files()

    # If this looks like an Azure AI Foundry *project* endpoint, use the Foundry-backed client.
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

    # Otherwise, assume direct Azure OpenAI configuration.
    return AzureOpenAIChatClient()


chat_client = _build_chat_client()

# NOTE: For DevUI, don't use `async with` around MCP tools. DevUI will manage
# the tool lifecycle and connections are established lazily on first use.
mcp_tool = MCPStreamableHTTPTool(
    name="fabric_de_mcp",
    url=_mcp_url(),
)

agent = ChatAgent(
    name="fabric_de_agent",
    chat_client=chat_client,
    tools=[mcp_tool],
    instructions=(
        "You are a Microsoft Fabric Data Engineering assistant. "
        "You can use the available MCP tools (fabric_de_mcp) to list workspaces, "
        "create items (Lakehouse, DataPipeline), and inspect/update items.\n\n"

        "Pipeline creation workflow:\n"
        "- Provide a valid pipeline definition JSON (Data Factory in Fabric format).\n"
        "- Then call fabric_de_mcp.create_pipeline or fabric_de_mcp.create_item "
        "with that definition.\n\n"
        "Tool use rules:\n"
        "- Prefer MCP tool calls over guessing.\n"
        "- Before calling tools that CREATE or UPDATE resources, describe what you plan to do "
        "and ask for confirmation unless the user explicitly told you to proceed.\n"
        "- Do not claim an item was created/updated unless the MCP tool call succeeded.\n"
        "- If a tool call fails, explain what failed and ask for the missing inputs.\n\n"
        "Auth note:\n"
        "- The MCP server supports an optional 'token' parameter, but when running locally it "
        "typically uses DefaultAzureCredential automatically.\n"
    ),
)
