from __future__ import annotations

from pathlib import Path

from .server import cli


def _load_env_file() -> None:
    """Load MCP-local .env if python-dotenv is installed.

    This keeps MCP config isolated from DevUI config by default.
    """

    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover
        return

    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

if __name__ == "__main__":
    _load_env_file()
    cli()
