"""
Role-Based Access Control dependency factories.

Usage in routers:
    from app.dependencies import CanWrite, CanDelete, RequireRole

    @router.post("/teams", dependencies=[Depends(CanWrite())])
    @router.delete("/teams/{id}", dependencies=[Depends(CanDelete())])
    @router.get("/admin", dependencies=[Depends(RequireRole("admin"))])

Role hierarchy (highest → lowest privilege):
    admin > manager > contributor > viewer
"""

from fastapi import Depends, HTTPException

from app.dependencies.auth import get_current_user
from app.models.user import User

VALID_ROLES = frozenset({"admin", "manager", "contributor", "viewer"})


def RequireRole(*roles: str):
    """
    Returns a FastAPI dependency that passes only if the authenticated
    user's role is one of the specified *roles*.  Raises 403 otherwise.
    """
    role_set = frozenset(roles)

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in role_set:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Role '{current_user.role}' is not permitted. "
                    f"Required: {sorted(role_set)}"
                ),
            )
        return current_user

    return _check


def CanWrite():
    """Admin / Manager / Contributor → create and update resources."""
    return RequireRole("admin", "manager", "contributor")


def CanDelete():
    """Admin / Manager only → delete resources.  Contributor is blocked."""
    return RequireRole("admin", "manager")


def CanManageUsers():
    """Admin only → create / modify users and roles."""
    return RequireRole("admin")
