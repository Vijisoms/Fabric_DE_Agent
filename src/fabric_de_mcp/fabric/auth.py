from __future__ import annotations

import logging

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential

from ..config import fabric_scope

logger = logging.getLogger(__name__)

# Module-level singleton so the credential chain is initialised once and
# tokens are cached across calls (avoids repeated CLI/IMDS probes).
_credential: DefaultAzureCredential | None = None


def _get_credential() -> DefaultAzureCredential:
    """Return a cached DefaultAzureCredential instance.

    DefaultAzureCredential tries these identities in order:
      1. Environment variables (service principal)
      2. Workload Identity (AKS)
      3. Managed Identity (Azure-hosted)
      4. Shared Token Cache (Windows)
      5. Azure CLI  (``az login``)
      6. Azure PowerShell
      7. Azure Developer CLI (``azd auth login``)

    Locally, ``az login`` is the most common path.
    In Azure Container Apps, Managed Identity is used automatically.
    """
    global _credential
    if _credential is None:
        _credential = DefaultAzureCredential()
    return _credential


def get_token(scope: str | None = None) -> str:
    """Acquire a bearer token for the Fabric REST API.

    Uses ``DefaultAzureCredential.get_token()`` with the configured scope
    (default ``https://api.fabric.microsoft.com/.default``).  The token is
    suitable for passing as ``Authorization: Bearer <token>`` to Fabric REST
    endpoints.

    Parameters
    ----------
    scope:
        Override the default scope.  Normally you should leave this as
        ``None`` to use ``FABRIC_SCOPE`` from config.

    Returns
    -------
    str
        The raw access-token string.

    Raises
    ------
    azure.core.exceptions.ClientAuthenticationError
        If none of the credential sources could authenticate.
    """
    target_scope = scope or fabric_scope()
    credential = _get_credential()
    try:
        access_token = credential.get_token(target_scope)
    except ClientAuthenticationError:
        logger.error(
            "DefaultAzureCredential could not authenticate. "
            "Ensure you are logged in via 'az login' or running "
            "under a managed identity."
        )
        raise
    return access_token.token
