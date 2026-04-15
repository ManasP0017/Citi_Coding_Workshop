"""
Server-Sent Events connection manager.

Design:
  - Each connected client gets a dedicated asyncio.Queue (bounded, maxsize=50).
  - broadcast() puts a formatted SSE frame into every live queue.
  - stream() is an async generator the StreamingResponse drains; it emits
    queued events or a ': heartbeat' comment every HEARTBEAT_INTERVAL seconds
    so proxies / load-balancers don't close the idle connection.
  - Dead clients (full queue) are evicted silently.
  - All operations are safe within a single asyncio event loop (single-process
    uvicorn). For multi-worker deployments, swap the queue map for Redis pub/sub.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 20  # seconds


def _format_sse(event: str, resource: str, data: Any) -> str:
    """
    Encode one SSE frame.

    Wire format (per spec):
        event: <event-name>\n
        data: <json-payload>\n
        \n
    """
    payload = json.dumps({
        "event":    event,
        "resource": resource,
        "data":     data,
        "ts":       datetime.now(timezone.utc).isoformat(),
    })
    return f"event: {event}\ndata: {payload}\n\n"


class SSEManager:
    def __init__(self) -> None:
        self._clients: dict[str, asyncio.Queue] = {}

    @property
    def client_count(self) -> int:
        return len(self._clients)

    # ── Connection lifecycle ───────────────────────────────────────────────

    def add_client(self, client_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=50)
        self._clients[client_id] = q
        logger.info("SSE client connected  id=%s total=%d", client_id, len(self._clients))
        return q

    def remove_client(self, client_id: str) -> None:
        self._clients.pop(client_id, None)
        logger.info("SSE client disconnected id=%s total=%d", client_id, len(self._clients))

    # ── Broadcasting ──────────────────────────────────────────────────────

    async def broadcast(self, event: str, resource: str, data: Any) -> None:
        """Push an event frame to every connected SSE client."""
        if not self._clients:
            return
        frame = _format_sse(event, resource, data)
        dead: list[str] = []
        for client_id, q in list(self._clients.items()):
            try:
                q.put_nowait(frame)
            except asyncio.QueueFull:
                logger.warning("SSE queue full, evicting client %s", client_id)
                dead.append(client_id)
        for client_id in dead:
            self.remove_client(client_id)

    # ── Streaming generator ───────────────────────────────────────────────

    async def stream(self, client_id: str) -> AsyncGenerator[str, None]:
        """
        Async generator consumed by FastAPI's StreamingResponse.
        Yields SSE frames from the client's queue; emits a heartbeat comment
        when idle to prevent proxy timeouts.
        """
        q = self._clients.get(client_id)
        if q is None:
            return

        # Handshake event — lets the frontend confirm auth succeeded
        yield _format_sse("connected", "system",
                          {"client_id": client_id, "msg": "Stream established"})

        while True:
            try:
                frame = await asyncio.wait_for(q.get(), timeout=HEARTBEAT_INTERVAL)
                yield frame
            except asyncio.TimeoutError:
                # SSE comment lines (': ...') are ignored by the browser but
                # keep the TCP connection alive through proxy idle-timeouts.
                yield ": heartbeat\n\n"
            except (asyncio.CancelledError, GeneratorExit):
                break


sse_manager = SSEManager()
