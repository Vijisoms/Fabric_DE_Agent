import argparse
import base64
import json
import logging
import pathlib
import sys
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

FABRIC_BASE_URL = "https://api.fabric.microsoft.com/v1"
DEFAULT_TIMEOUT = 30


class FabricApiError(RuntimeError):
    """Raised for non-success responses from the Fabric REST API."""


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def read_definition_payload(source: pathlib.Path) -> str:
    if str(source) == "-":
        payload = sys.stdin.read()
        if not payload:
            raise FabricApiError("STDIN is empty; provide a pipeline definition.")
        return payload
    try:
        return source.read_text(encoding="utf-8")
    except OSError as exc:
        raise FabricApiError(f"Failed to read pipeline definition: {exc}") from exc


def encode_definition(source: pathlib.Path) -> dict:
    payload = read_definition_payload(source)
    encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    return {
        "parts": [
            {
                "path": "pipeline-content.json",
                "payloadType": "InlineBase64",
                "payload": encoded,
            }
        ]
    }


def build_session(retries: int, backoff: float) -> requests.Session:
    retry_config = Retry(
        total=retries,
        status_forcelist=(408, 409, 429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST", "PATCH", "DELETE"),
        backoff_factor=backoff,
    )
    adapter = HTTPAdapter(max_retries=retry_config)
    session = requests.Session()
    session.mount("https://", adapter)
    return session


def create_pipeline(
    workspace_id: str,
    token: str,
    display_name: str,
    description: str,
    definition_path: Optional[pathlib.Path],
    timeout: int,
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

    url = f"{FABRIC_BASE_URL}/workspaces/{workspace_id}/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = session.post(url, headers=headers, json=payload, timeout=timeout)
    if response.status_code not in (200, 201, 202):
        raise FabricApiError(
            f"Fabric API error {response.status_code}: {response.text}"
        )
    return response.json()


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be a positive integer.")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be a positive number.")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Fabric Data Pipeline via REST API."
    )
    parser.add_argument("--workspace", required=True, help="Workspace ID (GUID).")
    parser.add_argument(
        "--token",
        required=True,
        help="Bearer token with Workspace.ReadWrite.All or Item.ReadWrite.All.",
    )
    parser.add_argument(
        "--definition",
        type=pathlib.Path,
        help="Path to pipeline JSON definition (use '-' to read from STDIN).",
    )
    parser.add_argument(
        "--name",
        default="pipeline_wait_one_hour",
        help="Display name for the pipeline item.",
    )
    parser.add_argument(
        "--description",
        default="Fabric pipeline created via script.",
        help="Pipeline description.",
    )
    parser.add_argument(
        "--timeout",
        type=positive_int,
        default=DEFAULT_TIMEOUT,
        help="Request timeout in seconds.",
    )
    parser.add_argument(
        "--retries",
        type=positive_int,
        default=3,
        help="Number of automatic retries for transient failures.",
    )
    parser.add_argument(
        "--backoff",
        type=positive_float,
        default=0.5,
        help="Backoff factor (seconds) between retries.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging for request diagnostics.",
    )

    args = parser.parse_args()
    configure_logging(args.verbose)

    result = create_pipeline(
        workspace_id=args.workspace,
        token=args.token,
        display_name=args.name,
        description=args.description,
        definition_path=args.definition,
        timeout=args.timeout,
        retries=args.retries,
        backoff=args.backoff,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except FabricApiError as exc:
        logging.error(exc)
        sys.exit(1)
    