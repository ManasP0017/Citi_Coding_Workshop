"""Backward-compat shim — import from app.core.logging instead."""
from app.core.logging import setup_logging, JsonFormatter  # noqa: F401
