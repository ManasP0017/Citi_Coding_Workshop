"""
Top-level dependencies package.
Composable FastAPI dependency factories used across all routers.
"""

from app.dependencies.auth import get_current_user                      # noqa: F401
from app.dependencies.rbac import RequireRole, CanWrite, CanDelete, CanManageUsers  # noqa: F401
