from __future__ import annotations

import argparse
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "mcp.server.fastmcp is required. Install with: pip install \"mcp[fastmcp]\""
    ) from exc

from .fabric.api import create_lakehouse as api_create_lakehouse
from .fabric.api import create_pipeline as api_create_pipeline
from .fabric.auth import get_token

app = FastMCP("FAB_DE")


@app.tool()
def create_pipeline(
    workspace_id: str,
    name: str,
    token: Optional[str] = None,
    description: str = "Fabric pipeline created via MCP",
    definition_path: Optional[str] = None,
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Create a Fabric pipeline item. Provide definition_path for base64 inlined JSON."""
    bearer = token or get_token()
    return api_create_pipeline(
        workspace_id=workspace_id,
        display_name=name,
        token=bearer,
        description=description,
        definition_path=definition_path,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


@app.tool()
def create_lakehouse(
    workspace_id: str,
    name: str,
    token: Optional[str] = None,
    description: str = "Lakehouse created via MCP",
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> dict:
    """Create a Fabric Lakehouse item."""
    bearer = token or get_token()
    return api_create_lakehouse(
        workspace_id=workspace_id,
        display_name=name,
        token=bearer,
        description=description,
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
