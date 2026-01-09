from __future__ import annotations

from azure.identity import DefaultAzureCredential

from ..config import fabric_scope


def get_token(scope: str | None = None) -> str:
    """Get a bearer token using DefaultAzureCredential (CLI, Managed Identity, etc.)."""
    credential = DefaultAzureCredential()
    return credential.get_token(scope or fabric_scope()).token
