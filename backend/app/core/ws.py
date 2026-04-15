"""
WebSocket connection manager for real-time event broadcasting.

Every mutating operation (create / update / delete) in a service
calls `ws_manager.broadcast(event)` so all connected clients are
notified instantly.

Event envelope:
    {
        "event":    "member.created" | "team.updated" | ...
        "resource": "member" | "team" | "achievement"
        "data":     { ...serialised payload... }
    }
"""

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._active.append(ws)
        logger.info("WS client connected. Total: %d", len(self._active))

    def disconnect(self, ws: WebSocket) -> None:
        self._active.remove(ws)
        logger.info("WS client disconnected. Total: %d", len(self._active))

    async def broadcast(self, event: str, resource: str, data: Any) -> None:
        if not self._active:
            return
        message = json.dumps({"event": event, "resource": resource, "data": data})
        dead: list[WebSocket] = []
        for ws in self._active:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._active.remove(ws)


ws_manager = ConnectionManager()
