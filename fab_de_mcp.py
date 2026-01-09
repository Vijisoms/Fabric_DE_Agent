"""FAB_DE MCP server exposing Fabric pipeline and lakehouse creation.

Implements a streamable MCP server using the Model Context Protocol Python SDK.
- Tool: create_pipeline
- Tool: create_lakehouse
- Token: optional; falls back to Azure CLI default credentials (az account get-access-token).
"""
from __future__ import annotations

import base64
import json
import pathlib
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry
from azure.identity import DefaultAzureCredential

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "mcp.server.fastmcp is required. Install with: pip install \"mcp[fastmcp]\""
    ) from exc

FABRIC_BASE_URL = "https://api.fabric.microsoft.com/v1"

app = FastMCP("FAB_DE")


class FabricApiError(Exception):
    """Raised when Fabric API returns a non-success status."""

    def __init__(self, status_code: int, body: str):
        super().__init__(f"Fabric API error {status_code}: {body}")
        self.status_code = status_code
        self.body = body


def get_token(scope: str = "https://api.fabric.microsoft.com/.default") -> str:
    """Get a bearer token using DefaultAzureCredential (CLI, managed identity, etc.)."""
    credential = DefaultAzureCredential()
    return credential.get_token(scope).token


def build_session(timeout: float, retries: int, backoff: float) -> requests.Session:
    retry_cfg = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(408, 409, 429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS", "POST", "PATCH", "DELETE"),
    )
    adapter = HTTPAdapter(max_retries=retry_cfg)
    session = requests.Session()
    session.mount("https://", adapter)
    return session


def encode_definition(definition_path: str) -> dict:
    path = pathlib.Path(definition_path)
    payload = path.read_text(encoding="utf-8")
    encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    return {
        "parts": [
            {
                "path": path.name,
                "payloadType": "InlineBase64",
                "payload": encoded,
            }
        ]
    }


def _create_pipeline(
    workspace_id: str,
    display_name: str,
    token: str,
    description: str,
    definition_path: Optional[str],
    timeout: float,
    retries: int,
    backoff: float,
) -> dict:
    session = build_session(timeout=timeout, retries=retries, backoff=backoff)
    payload: dict = {
        "displayName": display_name,
        "description": description,
        "type": "DataPipeline",
    }
    if definition_path:
        payload["definition"] = encode_definition(definition_path)

    url = f"{FABRIC_BASE_URL}/workspaces/{workspace_id}/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = session.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code not in (200, 201, 202):
        raise FabricApiError(resp.status_code, resp.text)
    return resp.json()


def _create_lakehouse(
    workspace_id: str,
    display_name: str,
    token: str,
    description: Optional[str],
    timeout: float,
    retries: int,
    backoff: float,
) -> dict:
    session = build_session(timeout=timeout, retries=retries, backoff=backoff)
    payload: dict = {"displayName": display_name, "type": "Lakehouse"}
    if description:
        payload["description"] = description

    url = f"{FABRIC_BASE_URL}/workspaces/{workspace_id}/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = session.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code not in (200, 201, 202):
        raise FabricApiError(resp.status_code, resp.text)
    return resp.json()


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
    return _create_pipeline(
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
    """Create a Fabric Lakehouse item (schema enabled by default)."""
    bearer = token or get_token()
    return _create_lakehouse(
        workspace_id=workspace_id,
        display_name=name,
        token=bearer,
        description=description,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )


if __name__ == "__main__":  # pragma: no cover
    app.run(transport="streamable-http")
