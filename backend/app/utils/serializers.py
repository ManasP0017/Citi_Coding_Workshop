"""Helpers to convert SQLAlchemy row instances to plain dicts."""

from datetime import datetime


def model_to_dict(row) -> dict:
    d = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d
