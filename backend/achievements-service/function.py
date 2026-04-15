"""
Achievements service Lambda handler.

Routes:
  POST   /achievements-service         — create an achievement
  GET    /achievements-service         — list achievements (optional ?search=&team_id=&month=&year=)
  GET    /achievements-service/{id}    — get achievement by id
  PUT    /achievements-service/{id}    — update achievement
  DELETE /achievements-service/{id}    — delete achievement
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone

import jwt
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── Config ──────────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "changeme-super-secret")
JWT_ALGORITHM = "HS256"

PG_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASS", "postgres123"),
    "dbname": os.getenv("POSTGRES_NAME", "postgres"),
    "connect_timeout": 15,
}

WRITE_ROLES = {"admin", "manager", "contributor"}
DELETE_ROLES = {"admin", "manager"}
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
}

_conn = None


def _get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(**PG_CONFIG)
        _conn.autocommit = False
        _ensure_tables(_conn)
    return _conn


def _ensure_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id          VARCHAR(36) PRIMARY KEY,
                title       VARCHAR(255) NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                team_id     VARCHAR(36) NOT NULL,
                month       VARCHAR(20) NOT NULL,
                year        INTEGER NOT NULL,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
    conn.commit()


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}


def _authenticate(event):
    headers = event.get("headers") or {}
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    token = auth[7:] if auth.startswith("Bearer ") else None
    if not token:
        return None
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def _parse_body(event):
    body = event.get("body", "{}")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body or {}


def _extract_id(path):
    """Extract resource UUID from path. Works with both /uuid and /api/service/uuid."""
    parts = [p for p in path.strip("/").split("/") if p]
    if not parts:
        return None
    last = parts[-1]
    if len(last) == 36 and last.count("-") == 4:
        return last
    return None


def _row_to_dict(row, columns):
    d = dict(zip(columns, row))
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


ACH_COLS = ["id", "title", "description", "team_id", "month", "year", "created_at", "updated_at"]


# ── Route handlers ──────────────────────────────────────────────────
def _create_achievement(event, user):
    if user["role"] not in WRITE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    data = _parse_body(event)
    title = (data.get("title") or "").strip()
    team_id = data.get("team_id") or ""
    month = data.get("month") or ""
    year = data.get("year")

    if not title or not team_id or not month or year is None:
        return _response(400, {"error": "title, team_id, month, and year are required"})

    ach_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO achievements
                   (id, title, description, team_id, month, year, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (ach_id, title, data.get("description", ""), team_id, month, int(year), now, now),
            )
        conn.commit()
        return _response(201, {"message": "Achievement created successfully", "id": ach_id})
    except Exception:
        conn.rollback()
        raise


def _list_achievements(event, user):
    params = event.get("queryStringParameters") or {}
    search = params.get("search")
    team_id = params.get("team_id")
    month = params.get("month")
    year = params.get("year")

    conn = _get_conn()
    with conn.cursor() as cur:
        query = "SELECT " + ", ".join(ACH_COLS) + " FROM achievements WHERE 1=1"
        args = []
        if search:
            query += " AND (title ILIKE %s OR description ILIKE %s)"
            args += [f"%{search}%", f"%{search}%"]
        if team_id:
            query += " AND team_id = %s"
            args.append(team_id)
        if month:
            query += " AND month = %s"
            args.append(month)
        if year:
            query += " AND year = %s"
            args.append(int(year))
        query += " ORDER BY year DESC, month"
        cur.execute(query, args)
        rows = cur.fetchall()

    achievements = [_row_to_dict(r, ACH_COLS) for r in rows]
    return _response(200, {"achievements": achievements})


def _get_achievement(event, user, ach_id):
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT " + ", ".join(ACH_COLS) + " FROM achievements WHERE id = %s",
            (ach_id,),
        )
        row = cur.fetchone()
    if not row:
        return _response(404, {"error": "Achievement not found"})
    return _response(200, _row_to_dict(row, ACH_COLS))


def _update_achievement(event, user, ach_id):
    if user["role"] not in WRITE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    data = _parse_body(event)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM achievements WHERE id = %s", (ach_id,))
            if not cur.fetchone():
                conn.rollback()
                return _response(404, {"error": "Achievement not found"})

            sets, args = [], []
            for field in ["title", "description", "team_id", "month"]:
                if field in data and data[field] is not None:
                    sets.append(f"{field} = %s")
                    args.append(data[field])
            if "year" in data and data["year"] is not None:
                sets.append("year = %s")
                args.append(int(data["year"]))
            if sets:
                sets.append("updated_at = %s")
                args.append(datetime.now(timezone.utc))
                args.append(ach_id)
                cur.execute(f"UPDATE achievements SET {', '.join(sets)} WHERE id = %s", args)
        conn.commit()
        return _response(200, {"message": "Achievement updated successfully"})
    except Exception:
        conn.rollback()
        raise


def _delete_achievement(event, user, ach_id):
    if user["role"] not in DELETE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM achievements WHERE id = %s", (ach_id,))
            if not cur.fetchone():
                conn.rollback()
                return _response(404, {"error": "Achievement not found"})
            cur.execute("DELETE FROM achievements WHERE id = %s", (ach_id,))
        conn.commit()
        return _response(204, {})
    except Exception:
        conn.rollback()
        raise


# ── Lambda entry point ──────────────────────────────────────────────
def handler(event, context=None):
    logger.info("achievements-service event: %s", json.dumps(event, default=str))

    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("path") or event.get("rawPath") or ""

    if method == "OPTIONS":
        return _response(200, {})

    user = _authenticate(event)
    if not user:
        return _response(401, {"error": "Not authenticated"})

    try:
        ach_id = _extract_id(path)

        if method == "POST" and not ach_id:
            return _create_achievement(event, user)
        elif method == "GET" and not ach_id:
            return _list_achievements(event, user)
        elif method == "GET" and ach_id:
            return _get_achievement(event, user, ach_id)
        elif method == "PUT" and ach_id:
            return _update_achievement(event, user, ach_id)
        elif method == "DELETE" and ach_id:
            return _delete_achievement(event, user, ach_id)
        else:
            return _response(404, {"error": "Not found"})
    except Exception as e:
        logger.exception("achievements-service error")
        return _response(500, {"error": "Internal server error", "message": str(e)})


if __name__ == "__main__":
    print(handler({"httpMethod": "GET", "path": "/achievements-service", "headers": {}}))
