"""CLI to create a Fabric Lakehouse item via REST.

- Uses default Azure credentials via `az account get-access-token` when `--token` is not provided.
- Includes retries, backoff, and timeout controls for resilience.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry
from azure.identity import DefaultAzureCredential


class FabricApiError(Exception):
    """Raised when Fabric API returns a non-success status."""

    def __init__(self, status_code: int, body: str):
        super().__init__(f"Fabric API error {status_code}: {body}")
        self.status_code = status_code
        self.body = body


def get_token(scope: str = "https://api.fabric.microsoft.com/.default") -> str:
    """Fetch a bearer token using DefaultAzureCredential (CLI, Managed Identity, etc.)."""
    credential = DefaultAzureCredential()
    return credential.get_token(scope).token


def build_session(timeout: float, retries: int, backoff: float) -> requests.Session:
    retry_cfg = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS", "POST", "PATCH"),
    )
    adapter = HTTPAdapter(max_retries=retry_cfg)

    session = requests.Session()
    session.mount("https://", adapter)
    session.request = session.request  # type: ignore[attr-defined]
    session.timeout = timeout  # type: ignore[attr-defined]
    return session


def create_lakehouse(
    workspace_id: str,
    display_name: str,
    token: str,
    description: Optional[str],
    timeout: float,
    retries: int,
    backoff: float,
    verbose: bool,
) -> dict:
    session = build_session(timeout, retries, backoff)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"displayName": display_name, "type": "Lakehouse"}
    if description:
        payload["description"] = description

    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items"
    if verbose:
        sys.stderr.write(
            f"POST {url}\n" f"payload={json.dumps(payload)}\n" f"timeout={timeout}s retries={retries} backoff={backoff}\n"
        )

    resp = session.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code >= 400:
        raise FabricApiError(resp.status_code, resp.text)
    return resp.json()


def positive_float(value: str) -> float:
    f = float(value)
    if f <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return f


def non_negative_float(value: str) -> float:
    f = float(value)
    if f < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return f


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Fabric Lakehouse via REST API")
    parser.add_argument("--workspace", required=True, help="Workspace GUID")
    parser.add_argument("--name", required=True, help="Lakehouse display name")
    parser.add_argument("--description", help="Optional description")
    parser.add_argument("--token", help="Bearer token; if omitted uses Azure CLI default credentials")
    parser.add_argument(
        "--resource",
        default="https://api.fabric.microsoft.com/.default",
        help="AAD scope for token request (default: Fabric .default)",
    )
    parser.add_argument("--timeout", type=positive_float, default=30.0, help="Request timeout in seconds (default: 30)")
    parser.add_argument("--retries", type=int, default=3, help="Retry attempts for transient errors (default: 3)")
    parser.add_argument("--backoff", type=non_negative_float, default=0.5, help="Backoff factor for retries (default: 0.5)")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        bearer = args.token or get_token(args.resource)
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"Failed to acquire token via Azure CLI: {exc}\n{exc.stderr}\n")
        return 1

    try:
        result = create_lakehouse(
            workspace_id=args.workspace,
            display_name=args.name,
            token=bearer,
            description=args.description,
            timeout=args.timeout,
            retries=args.retries,
            backoff=args.backoff,
            verbose=args.verbose,
        )
    except FabricApiError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    except requests.RequestException as exc:
        sys.stderr.write(f"Request failed: {exc}\n")
        return 1

    sys.stdout.write(json.dumps(result, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
