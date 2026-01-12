from __future__ import annotations

import argparse
import os
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "mcp.server.fastmcp is required. Install with: pip install \"mcp[fastmcp]\""
    ) from exc

from .fabric import api as fabric_api
from .fabric.auth import get_token


def _fastmcp_host() -> str:
    # In Azure Container Apps, bind to all interfaces.
    return os.getenv("FASTMCP_HOST", "127.0.0.1")


def _fastmcp_port() -> int:
    # Many PaaS hosts (including ACA) provide PORT; prefer FASTMCP_PORT when set.
    return int(os.getenv("FASTMCP_PORT") or os.getenv("PORT") or "8000")


app = FastMCP("FAB_DE", host=_fastmcp_host(), port=_fastmcp_port())


@app.tool()
def create_pipeline(
    workspace_id: str,
    name: str,
    token: str = "",
    description: str = "Fabric pipeline created via MCP",
    definition_path: str = "",
    definition: Optional[dict] = None,
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Create a Fabric pipeline item. Provide definition_path for base64 inlined JSON."""
    bearer = token or get_token()
    return fabric_api.create_pipeline(
        workspace_id=workspace_id,
        display_name=name,
        token=bearer,
        description=description,
        definition_path=definition_path or None,
        definition=definition,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def create_lakehouse(
    workspace_id: str,
    name: str,
    token: str = "",
    description: str = "Lakehouse created via MCP",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Create a Fabric Lakehouse item."""
    bearer = token or get_token()
    return fabric_api.create_lakehouse(
        workspace_id=workspace_id,
        display_name=name,
        token=bearer,
        description=description,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def list_workspaces(
    token: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """List workspaces in the current Fabric tenant."""
    bearer = token or get_token()
    return fabric_api.list_workspaces(
        token=bearer,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def create_item(
    workspace_id: str,
    name: str,
    item_type: str,
    token: str = "",
    description: str = "",
    definition_path: str = "",
    definition: Optional[dict] = None,
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Create a Fabric item in a workspace.

    This is the generic creator for any supported Fabric item type (for example:
    `Lakehouse`, `Notebook`, `SparkJobDefinition`, `DataPipeline`).

    Notes:
    - This server intentionally does not expose delete APIs.
    - Provide `definition_path` to base64-inline a JSON definition file.
    """
    bearer = token or get_token()
    return fabric_api.create_item(
        workspace_id=workspace_id,
        display_name=name,
        item_type=item_type,
        token=bearer,
        description=description or None,
        definition_path=definition_path or None,
        definition=definition,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def list_items(
    workspace_id: str,
    token: str = "",
    continuation_url: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """List items in a Fabric workspace.

    If the response includes a continuation URI, pass it back as `continuation_url`
    to retrieve the next page.
    """
    bearer = token or get_token()
    return fabric_api.list_items(
        workspace_id=workspace_id,
        token=bearer,
        continuation_url=continuation_url or None,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def get_item(
    workspace_id: str,
    item_id: str,
    token: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Get Fabric item properties by workspace + item id."""
    bearer = token or get_token()
    return fabric_api.get_item(
        workspace_id=workspace_id,
        item_id=item_id,
        token=bearer,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def update_item(
    workspace_id: str,
    item_id: str,
    token: str = "",
    name: str = "",
    description: str = "",
    item_type: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Update Fabric item metadata (display name / description).

    This updates item properties (PATCH). For definition updates, use
    `update_item_definition`.
    """
    bearer = token or get_token()
    return fabric_api.update_item(
        workspace_id=workspace_id,
        item_id=item_id,
        token=bearer,
        display_name=name or None,
        description=description or None,
        item_type=item_type or None,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def get_item_definition(
    workspace_id: str,
    item_id: str,
    token: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Get the definition for a Fabric item (base64 parts)."""
    bearer = token or get_token()
    return fabric_api.get_item_definition(
        workspace_id=workspace_id,
        item_id=item_id,
        token=bearer,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def update_item_definition(
    workspace_id: str,
    item_id: str,
    token: str = "",
    name: str = "",
    item_type: str = "",
    definition_path: str = "",
    definition: Optional[dict] = None,
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Update a Fabric item's definition.

    Provide either:
    - `definition_path` (JSON file on disk, base64 inlined), or
    - `definition` (a pre-built dict in the Fabric definition format).
    """
    bearer = token or get_token()
    return fabric_api.update_item_definition(
        workspace_id=workspace_id,
        item_id=item_id,
        token=bearer,
        display_name=name or None,
        item_type=item_type or None,
        definition_path=definition_path or None,
        definition=definition or None,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def get_lakehouse(
    workspace_id: str,
    lakehouse_id: str,
    token: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Get lakehouse properties."""
    bearer = token or get_token()
    return fabric_api.get_lakehouse(
        workspace_id=workspace_id,
        lakehouse_id=lakehouse_id,
        token=bearer,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def list_lakehouse_tables(
    workspace_id: str,
    lakehouse_id: str,
    token: str = "",
    max_results: int = 0,
    continuation_url: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """List tables in a lakehouse.

    If the response includes a continuation URI, pass it back as `continuation_url`
    to retrieve the next page.
    """
    bearer = token or get_token()
    return fabric_api.list_lakehouse_tables(
        workspace_id=workspace_id,
        lakehouse_id=lakehouse_id,
        token=bearer,
        max_results=max_results or None,
        continuation_url=continuation_url or None,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def run_pipeline_job_instance(
    workspace_id: str,
    item_id: str,
    token: str = "",
    execution_data: Optional[dict] = None,
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Run a Data Factory pipeline (on-demand job instance)."""
    bearer = token or get_token()
    return fabric_api.run_pipeline_job_instance(
        workspace_id=workspace_id,
        item_id=item_id,
        token=bearer,
        execution_data=execution_data or None,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def get_pipeline_job_instance(
    workspace_id: str,
    item_id: str,
    job_instance_id: str,
    token: str = "",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Get status for a pipeline job instance."""
    bearer = token or get_token()
    return fabric_api.get_pipeline_job_instance(
        workspace_id=workspace_id,
        item_id=item_id,
        job_instance_id=job_instance_id,
        token=bearer,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


def cli(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the FAB_DE MCP server")
    parser.add_argument(
        "--transport",
        default="streamable-http",
        choices=["streamable-http"],
        help="MCP transport to use (default: streamable-http)",
    )
    args = parser.parse_args(argv)

    app.run(transport=args.transport)
