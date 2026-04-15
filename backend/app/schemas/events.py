"""
Server-Sent Event envelope schema.

Every message pushed over the /api/events stream uses this shape.
Frontend consumers can switch on `event` to decide what to refresh.
"""

from typing import Any
from pydantic import BaseModel


class EventMessage(BaseModel):
    event:    str   # e.g. "team.created" | "member.deleted" | "connected"
    resource: str   # "team" | "member" | "achievement" | "system"
    data:     Any   # serialised resource dict (or minimal {id} for deletes)
    ts:       str   # ISO-8601 UTC timestamp

    model_config = {"json_schema_extra": {
        "example": {
            "event":    "member.created",
            "resource": "member",
            "data":     {"id": "abc", "name": "Alice", "team_id": "xyz"},
            "ts":       "2026-04-15T09:00:00+00:00",
        }
    }}
