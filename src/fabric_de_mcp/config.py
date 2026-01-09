from __future__ import annotations

import os


def fabric_base_url() -> str:
    return os.getenv("FABRIC_BASE_URL", "https://api.fabric.microsoft.com/v1")


def fabric_scope() -> str:
    return os.getenv("FABRIC_SCOPE", "https://api.fabric.microsoft.com/.default")
