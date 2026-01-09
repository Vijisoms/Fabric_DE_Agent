from __future__ import annotations


class FabricApiError(RuntimeError):
    """Raised when Fabric API returns a non-success status."""

    def __init__(self, status_code: int, body: str):
        super().__init__(f"Fabric API error {status_code}: {body}")
        self.status_code = status_code
        self.body = body
