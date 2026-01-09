from __future__ import annotations

import base64
import pathlib
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from ..config import fabric_base_url
from .errors import FabricApiError


def build_session(*, retries: int, backoff: float) -> requests.Session:
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


def create_pipeline(
    *,
    workspace_id: str,
    display_name: str,
    token: str,
    description: str,
    definition_path: Optional[str],
    timeout: float,
    retries: int,
    backoff: float,
) -> dict:
    session = build_session(retries=retries, backoff=backoff)
    payload: dict = {
        "displayName": display_name,
        "description": description,
        "type": "DataPipeline",
    }
    if definition_path:
        payload["definition"] = encode_definition(definition_path)

    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = session.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code not in (200, 201, 202):
        raise FabricApiError(resp.status_code, resp.text)
    return resp.json()


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
    session = build_session(retries=retries, backoff=backoff)
    payload: dict = {"displayName": display_name, "type": "Lakehouse"}
    if description:
        payload["description"] = description

    url = f"{fabric_base_url()}/workspaces/{workspace_id}/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = session.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code not in (200, 201, 202):
        raise FabricApiError(resp.status_code, resp.text)
    return resp.json()
