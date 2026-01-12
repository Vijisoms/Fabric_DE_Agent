from __future__ import annotations

# DevUI directory discovery expects each agent directory to export `agent`.
from .agent import agent as agent

__all__ = ["agent"]
