"""Backward-compat shim — import from app.dependencies.rbac instead."""
from app.dependencies.rbac import (  # noqa: F401
    VALID_ROLES, RequireRole, CanWrite, CanDelete, CanManageUsers,
)
