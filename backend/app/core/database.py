"""
Canonical database module.
SQLAlchemy engine, session factory, and declarative Base.
Supports SQLite (local, no POSTGRES_HOST) and PostgreSQL (local/cloud).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def _configure_connection(dbapi_conn, _connection_record):
    if settings.is_sqlite:
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a scoped DB session, guaranteed to close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
