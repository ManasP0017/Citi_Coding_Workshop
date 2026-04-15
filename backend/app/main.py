"""
Team Management API — application entry point.

Startup order:
1. Logging configured
2. DB tables ensured (Alembic handles migrations; create_all is a safety net for dev)
3. Routers mounted
4. Exception handlers registered
5. WebSocket endpoint registered
"""

import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.ws import ws_manager
from app.core.logging import setup_logging
from app.utils.errors import register_exception_handlers
from app.routers import auth, teams, members, achievements, insights, health, events

setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

# ── Safety-net: ensure tables exist (migrations are the canonical path) ────
Base.metadata.create_all(bind=engine)

# ── App factory ────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(members.router)
app.include_router(achievements.router)
app.include_router(insights.router)
app.include_router(events.router)


# ── WebSocket — real-time event stream ────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()   # keep connection alive; client pings
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
