"""
Unified event broadcaster.

Routers call `broadcast(event, resource, data)` once;
this module fans the message out to every active transport:
  • SSE  — `app/core/sse.py`   (primary, for dashboards)
  • WebSocket — `app/core/ws.py` (secondary, kept for compatibility)

Adding Redis pub/sub or any other transport later requires changing
only this file.
"""

import asyncio
import logging
from typing import Any

from app.core.sse import sse_manager
from app.core.ws  import ws_manager

logger = logging.getLogger(__name__)


async def broadcast(event: str, resource: str, data: Any) -> None:
    """Fan the event out to all live SSE and WebSocket clients."""
    await asyncio.gather(
        sse_manager.broadcast(event, resource, data),
        ws_manager.broadcast(event, resource, data),
        return_exceptions=True,   # one failing transport must not kill the other
    )
