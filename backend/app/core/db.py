"""Backward-compat shim — import from app.core.database instead."""
from app.core.database import engine, SessionLocal, Base, get_db  # noqa: F401
