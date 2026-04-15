"""
SSE event-stream endpoint.

GET /api/events?token=<JWT>

Why token in query-string?
  The browser's native EventSource API cannot set custom HTTP headers.
  Passing the JWT as a query parameter is the standard workaround.
  The token is validated server-side before the stream opens; the URL
  should be treated as a secret (use HTTPS in production).

Usage from JavaScript:
    const es = new EventSource(
      `${API_BASE}/api/events?token=${localStorage.getItem('token')}`
    );
    es.addEventListener('team.created', e => {
      const payload = JSON.parse(e.data);
      // refresh your teams list or show a toast
    });
    es.addEventListener('connected', e => console.log('SSE ready', e.data));
    es.onerror = () => es.close();   // EventSource auto-reconnects by default
"""

import uuid
import logging

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.sse import sse_manager
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["events"])


async def _authenticate_token(
    token: str = Query(..., description="JWT access token (required: EventSource cannot set headers)"),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that validates a JWT supplied as a query-string parameter.
    Used only by the SSE endpoint — all other routes use the Authorization header.
    """
    payload = decode_access_token(token)
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get(
    "/events",
    summary="Real-time event stream (SSE)",
    description=(
        "Streams server-sent events for all mutations in the system. "
        "Requires a valid JWT supplied as `?token=<jwt>`. "
        "All authenticated roles receive all events."
    ),
    response_description="text/event-stream",
)
async def sse_events(
    request: Request,
    current_user: User = Depends(_authenticate_token),
):
    client_id = str(uuid.uuid4())
    sse_manager.add_client(client_id)

    logger.info(
        "SSE stream opened user=%s role=%s client=%s",
        current_user.email, current_user.role, client_id,
    )

    async def generator():
        try:
            async for frame in sse_manager.stream(client_id):
                # Check if client disconnected between yields
                if await request.is_disconnected():
                    logger.info("SSE client %s disconnected (request closed)", client_id)
                    break
                yield frame
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            sse_manager.remove_client(client_id)

    import asyncio
    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",       # disable nginx buffering
            "Connection":       "keep-alive",
        },
    )
