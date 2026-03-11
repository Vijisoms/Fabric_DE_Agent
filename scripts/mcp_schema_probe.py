"""Probe the local FastMCP server's generated tool schemas.

This is a dev-only helper script used to confirm that tool schemas are compatible
with strict MCP consumers (e.g., Azure AI Foundry Agents).

It starts the server as a subprocess, fetches the tool list via Streamable HTTP,
and prints the inputSchema for a requested tool.

Usage:
  python scripts/mcp_schema_probe.py create_pipeline

Defaults to probing create_pipeline.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from contextlib import closing

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


def _wait_for_port(host: str, port: int, *, timeout_s: float = 10.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with closing(socket.create_connection((host, port), timeout=0.5)):
                return
        except OSError as exc:
            last_err = exc
            time.sleep(0.1)
    raise RuntimeError(f"Server did not open {host}:{port} within {timeout_s}s") from last_err


async def _fetch_schema(tool_name: str) -> dict:
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (
        read,
        write,
        _get_session_id,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool = next((t for t in tools.tools if t.name == tool_name), None)
            if tool is None:
                raise SystemExit(f"Tool not found: {tool_name}. Available: {[t.name for t in tools.tools]}")
            return tool.inputSchema


def main() -> int:
    tool_name = sys.argv[1] if len(sys.argv) > 1 else "create_pipeline"

    proc = subprocess.Popen(
        [sys.executable, "-m", "fabric_de_mcp"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    try:
        _wait_for_port("127.0.0.1", 8000, timeout_s=15.0)
        schema = anyio.run(_fetch_schema, tool_name)
        print(json.dumps(schema, indent=2, sort_keys=True))
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
