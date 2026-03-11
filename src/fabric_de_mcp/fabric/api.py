from __future__ import annotations

import base64
import json
import pathlib
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from ..config import fabric_base_url
from .errors import FabricApiError


def build_session(*, retries: int, backoff: float) -> requests.Session:
    retry_cfg = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(408, 409, 429, 500, 502, 503, 504),
        # Exclude DELETE: this MCP server intentionally does not expose delete operations.
        allowed_methods=("HEAD", "GET", "OPTIONS", "POST", "PATCH"),
    )
    adapter = HTTPAdapter(max_retries=retry_cfg)
    session = requests.Session()
    session.mount("https://", adapter)
    return session


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _json_or_text(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except ValueError:
        text = (resp.text or "").strip()
        return {"text": text} if text else {}


def _request(
    session: requests.Session,
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    timeout: float,
    ok_statuses: tuple[int, ...],
    params: Optional[dict[str, Any]] = None,
    json: Optional[dict[str, Any]] = None,
) -> Any:
    resp = session.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        timeout=timeout,
    )
    if resp.status_code not in ok_statuses:
        raise FabricApiError(resp.status_code, resp.text)
    return _json_or_text(resp)


def _encode_part(payload: str | dict, *, filename: str) -> dict:
    if not isinstance(payload, str):
        payload = json.dumps(payload, ensure_ascii=False)
    encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    return {
        "path": filename,
        "payloadType": "InlineBase64",
        "payload": encoded,
    }


def encode_definition(definition_path: str) -> dict:
    path = pathlib.Path(definition_path)
    payload = path.read_text(encoding="utf-8")
    return {
        "parts": [
            _encode_part(payload, filename=path.name),
        ]
    }


def wrap_definition_payload(definition: dict, *, filename: str) -> dict:
    return {
        "parts": [
            _encode_part(definition, filename=filename),
        ]
    }


def wrap_pipeline_definition(
    definition: dict,
    *,
    display_name: Optional[str],
    description: Optional[str],
) -> dict:
    platform_payload: dict[str, Any] = {
        "$schema": (
            "https://developer.microsoft.com/json-schemas/fabric/"
            "gitIntegration/platformProperties/2.0.0/schema.json"
        ),
        "metadata": {
            "type": "DataPipeline",
        },
        "config": {
            "version": "2.0",
            "logicalId": "00000000-0000-0000-0000-000000000000",
        },
    }
    if display_name:
        platform_payload["metadata"]["displayName"] = display_name
    if description:
        platform_payload["metadata"]["description"] = description

    return {
        "parts": [
            _encode_part(definition, filename="pipeline-content.json"),
            _encode_part(platform_payload, filename=".platform"),
        ]
    }


def create_item(
    *,
    workspace_id: str,
    display_name: str,
    item_type: str,
    token: str,
    description: Optional[str],
    definition_path: Optional[str],
    definition: Optional[dict[str, Any]] = None,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Create a Fabric item in a workspace.

    Fabric supports creating many item types through the unified endpoint:
    POST /v1/workspaces/{workspaceId}/items
    """
    if definition_path and definition:
        raise ValueError("Provide only one of definition_path or definition")

    session = build_session(retries=retries, backoff=backoff)
    payload: dict[str, Any] = {
        "displayName": display_name,
        "type": item_type,
    }
    if description:
        payload["description"] = description
    if definition_path:
        payload["definition"] = encode_definition(definition_path)
    elif definition is not None:
        payload["definition"] = definition

    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items"
    return _request(
        session,
        "POST",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200, 201, 202),
        json=payload,
    )


def create_pipeline(
    *,
    workspace_id: str,
    display_name: str,
    token: str,
    description: str,
    definition_path: Optional[str],
    definition: Optional[dict[str, Any]] = None,
    timeout: float,
    retries: int,
    backoff: float,
) -> dict:
    definition_payload = definition
    if definition is not None and "parts" not in definition:
        definition_payload = wrap_pipeline_definition(
            definition,
            display_name=display_name,
            description=description,
        )
    resp = create_item(
        workspace_id=workspace_id,
        display_name=display_name,
        item_type="DataPipeline",
        token=token,
        description=description,
        definition_path=definition_path,
        definition=definition_payload,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )
    return resp  # type: ignore[return-value]


def create_lakehouse(
    *,
    workspace_id: str,
    display_name: str,
    token: str,
    description: Optional[str],
    timeout: float,
    retries: int,
    backoff: float,
) -> dict:
    resp = create_item(
        workspace_id=workspace_id,
        display_name=display_name,
        item_type="Lakehouse",
        token=token,
        description=description,
        definition_path=None,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )
    return resp  # type: ignore[return-value]


def list_items(
    *,
    workspace_id: str,
    token: str,
    timeout: float,
    retries: int,
    backoff: float,
    continuation_url: Optional[str] = None,
) -> Any:
    """List Fabric items in a workspace.

    GET /v1/workspaces/{workspaceId}/items
    If the service returns a continuation URI, pass it back via continuation_url.
    """
    session = build_session(retries=retries, backoff=backoff)
    url = continuation_url or f"{fabric_base_url()}/workspaces/{workspace_id}/items"
    return _request(
        session,
        "GET",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200,),
    )


def get_item(
    *,
    workspace_id: str,
    item_id: str,
    token: str,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Get item properties.

    GET /v1/workspaces/{workspaceId}/items/{itemId}
    """
    session = build_session(retries=retries, backoff=backoff)
    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items/{item_id}"
    return _request(
        session,
        "GET",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200,),
    )


def update_item(
    *,
    workspace_id: str,
    item_id: str,
    token: str,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    item_type: Optional[str] = None,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Update item properties (metadata).

    PATCH /v1/workspaces/{workspaceId}/items/{itemId}
    """
    payload: dict[str, Any] = {}
    if display_name is not None:
        payload["displayName"] = display_name
    if description is not None:
        payload["description"] = description
    if item_type is not None:
        payload["type"] = item_type

    session = build_session(retries=retries, backoff=backoff)
    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items/{item_id}"
    return _request(
        session,
        "PATCH",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200, 202),
        json=payload,
    )


def get_item_definition(
    *,
    workspace_id: str,
    item_id: str,
    token: str,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Get the item definition.

    POST /v1/workspaces/{workspaceId}/items/{itemId}/getDefinition
    """
    session = build_session(retries=retries, backoff=backoff)
    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items/{item_id}/getDefinition"
    return _request(
        session,
        "POST",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200,),
    )


def update_item_definition(
    *,
    workspace_id: str,
    item_id: str,
    token: str,
    display_name: Optional[str] = None,
    item_type: Optional[str] = None,
    definition_path: Optional[str] = None,
    definition: Optional[dict[str, Any]] = None,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Update the item definition.

    POST /v1/workspaces/{workspaceId}/items/{itemId}/updateDefinition
    Provide either definition_path or a pre-built definition dict.
    """
    if definition_path and definition:
        raise ValueError("Provide only one of definition_path or definition")

    payload: dict[str, Any] = {}
    if display_name is not None:
        payload["displayName"] = display_name
    if item_type is not None:
        payload["type"] = item_type
    if definition_path is not None:
        payload["definition"] = encode_definition(definition_path)
    elif definition is not None:
        if "parts" not in definition:
            if item_type == "DataPipeline":
                payload["definition"] = wrap_pipeline_definition(
                    definition,
                    display_name=display_name,
                    description=None,
                )
            else:
                payload["definition"] = wrap_definition_payload(
                    definition,
                    filename="pipeline-content.json",
                )
        else:
            payload["definition"] = definition

    session = build_session(retries=retries, backoff=backoff)
    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items/{item_id}/updateDefinition"
    return _request(
        session,
        "POST",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200, 202),
        json=payload,
    )


def get_lakehouse(
    *,
    workspace_id: str,
    lakehouse_id: str,
    token: str,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Get lakehouse properties.

    GET /v1/workspaces/{workspaceId}/lakehouses/{lakehouseId}
    """
    session = build_session(retries=retries, backoff=backoff)
    url = f"{fabric_base_url()}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
    return _request(
        session,
        "GET",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200,),
    )


def list_lakehouse_tables(
    *,
    workspace_id: str,
    lakehouse_id: str,
    token: str,
    timeout: float,
    retries: int,
    backoff: float,
    max_results: Optional[int] = None,
    continuation_url: Optional[str] = None,
) -> Any:
    """List tables in a lakehouse.

    GET /v1/workspaces/{workspaceId}/lakehouses/{lakehouseId}/tables
    Supports pagination via continuation URI from the service.
    """
    session = build_session(retries=retries, backoff=backoff)
    url = continuation_url or (
        f"{fabric_base_url()}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables"
    )
    params: dict[str, Any] = {}
    if max_results is not None:
        params["maxResults"] = max_results
    return _request(
        session,
        "GET",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200,),
        params=params or None,
    )


def run_pipeline_job_instance(
    *,
    workspace_id: str,
    item_id: str,
    token: str,
    execution_data: Optional[dict[str, Any]] = None,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Run a pipeline job instance on-demand.

    POST /v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances?jobType=Pipeline
    """
    session = build_session(retries=retries, backoff=backoff)
    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items/{item_id}/jobs/instances"
    payload: dict[str, Any] = {}
    if execution_data is not None:
        payload["executionData"] = execution_data
    return _request(
        session,
        "POST",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200, 202),
        params={"jobType": "Pipeline"},
        json=payload or None,
    )


def get_pipeline_job_instance(
    *,
    workspace_id: str,
    item_id: str,
    job_instance_id: str,
    token: str,
    timeout: float,
    retries: int,
    backoff: float,
) -> Any:
    """Get a pipeline job instance status.

    GET /v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances/{jobInstanceId}
    """
    session = build_session(retries=retries, backoff=backoff)
    url = (
        f"{fabric_base_url()}/workspaces/{workspace_id}/items/{item_id}"
        f"/jobs/instances/{job_instance_id}"
    )
    return _request(
        session,
        "GET",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200,),
    )


def list_workspaces(
    *,
    token: str,
    timeout: float,
    retries: int,
    backoff: float,
) -> dict:
    session = build_session(retries=retries, backoff=backoff)
    url = f"{fabric_base_url()}/workspaces"
    resp = _request(
        session,
        "GET",
        url,
        headers=_headers(token),
        timeout=timeout,
        ok_statuses=(200,),
    )
    return resp  # type: ignore[return-value]
