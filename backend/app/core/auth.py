"""Backward-compat shim — import from app.core.security instead."""
from app.core.security import (  # noqa: F401
    hash_password, verify_password,
    create_access_token, decode_access_token,
)
