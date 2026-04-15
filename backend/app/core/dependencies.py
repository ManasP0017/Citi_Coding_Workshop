"""Backward-compat shim — import from app.dependencies.auth instead."""
from app.dependencies.auth import get_current_user  # noqa: F401
