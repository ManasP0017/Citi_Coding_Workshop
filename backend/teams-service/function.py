"""
Teams service Lambda handler.

Routes:
  POST   /teams-service         — create a team
  GET    /teams-service         — list teams (optional ?search=&location=)
  GET    /teams-service/{id}    — get team by id
  PUT    /teams-service/{id}    — update team
  DELETE /teams-service/{id}    — delete team
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

import jwt
import psycopg2
import psycopg2.extras

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
            CREATE TABLE IF NOT EXISTS teams (
                id                     VARCHAR(36) PRIMARY KEY,
                name                   VARCHAR(255) NOT NULL,
                location               VARCHAR(255) NOT NULL DEFAULT '',
                organization_leader_id VARCHAR(36),
                description            TEXT NOT NULL DEFAULT '',
                created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS members (
                id              VARCHAR(36) PRIMARY KEY,
                name            VARCHAR(255) NOT NULL,
                email           VARCHAR(255) UNIQUE NOT NULL,
                team_id         VARCHAR(36),
                role            VARCHAR(100) NOT NULL DEFAULT 'member',
                is_team_leader  BOOLEAN NOT NULL DEFAULT FALSE,
                is_direct_staff BOOLEAN NOT NULL DEFAULT TRUE,
                location        VARCHAR(255) NOT NULL DEFAULT '',
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
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
    # UUIDs are 36 chars with 4 dashes (e.g., 550e8400-e29b-41d4-a716-446655440000)
    if len(last) == 36 and last.count("-") == 4:
        return last
    return None


def _row_to_dict(row, columns):
    d = dict(zip(columns, row))
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


TEAM_COLS = ["id", "name", "location", "organization_leader_id", "description", "created_at", "updated_at"]


# ── Route handlers ──────────────────────────────────────────────────
def _create_team(event, user):
    if user["role"] not in WRITE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    data = _parse_body(event)
    name = (data.get("name") or "").strip()
    if not name:
        return _response(400, {"error": "Team name is required"})

    team_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO teams (id, name, location, organization_leader_id, description, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (team_id, name, data.get("location", ""),
                 data.get("organization_leader_id"), data.get("description", ""), now, now),
            )
        conn.commit()
        return _response(201, {"message": "Team created successfully", "id": team_id})
    except Exception:
        conn.rollback()
        raise


def _list_teams(event, user):
    params = event.get("queryStringParameters") or {}
    search = params.get("search")
    location = params.get("location")

    conn = _get_conn()
    with conn.cursor() as cur:
        query = "SELECT " + ", ".join(TEAM_COLS) + " FROM teams WHERE 1=1"
        args = []
        if search:
            query += " AND (name ILIKE %s OR description ILIKE %s)"
            args += [f"%{search}%", f"%{search}%"]
        if location:
            query += " AND location ILIKE %s"
            args.append(f"%{location}%")
        query += " ORDER BY name"
        cur.execute(query, args)
        rows = cur.fetchall()

    teams = [_row_to_dict(r, TEAM_COLS) for r in rows]
    return _response(200, {"teams": teams})


def _get_team(event, user, team_id):
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT " + ", ".join(TEAM_COLS) + " FROM teams WHERE id = %s", (team_id,)
        )
        row = cur.fetchone()
    if not row:
        return _response(404, {"error": "Team not found"})
    return _response(200, _row_to_dict(row, TEAM_COLS))


def _update_team(event, user, team_id):
    if user["role"] not in WRITE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    data = _parse_body(event)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM teams WHERE id = %s", (team_id,))
            if not cur.fetchone():
                conn.rollback()
                return _response(404, {"error": "Team not found"})

            sets, args = [], []
            for field in ["name", "location", "organization_leader_id", "description"]:
                if field in data and data[field] is not None:
                    sets.append(f"{field} = %s")
                    args.append(data[field])
            if sets:
                sets.append("updated_at = %s")
                args.append(datetime.now(timezone.utc))
                args.append(team_id)
                cur.execute(f"UPDATE teams SET {', '.join(sets)} WHERE id = %s", args)
        conn.commit()
        return _response(200, {"message": "Team updated successfully"})
    except Exception:
        conn.rollback()
        raise


def _delete_team(event, user, team_id):
    if user["role"] not in DELETE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM teams WHERE id = %s", (team_id,))
            if not cur.fetchone():
                conn.rollback()
                return _response(404, {"error": "Team not found"})
            cur.execute("UPDATE members SET team_id = NULL WHERE team_id = %s", (team_id,))
            cur.execute("DELETE FROM achievements WHERE team_id = %s", (team_id,))
            cur.execute("DELETE FROM teams WHERE id = %s", (team_id,))
        conn.commit()
        return _response(204, {})
    except Exception:
        conn.rollback()
        raise


# ── Lambda entry point ──────────────────────────────────────────────
def handler(event, context=None):
    logger.info("teams-service event: %s", json.dumps(event, default=str))

    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("path") or event.get("rawPath") or ""

    if method == "OPTIONS":
        return _response(200, {})

    user = _authenticate(event)
    if not user:
        return _response(401, {"error": "Not authenticated"})

    try:
        team_id = _extract_id(path)

        if method == "POST" and not team_id:
            return _create_team(event, user)
        elif method == "GET" and not team_id:
            return _list_teams(event, user)
        elif method == "GET" and team_id:
            return _get_team(event, user, team_id)
        elif method == "PUT" and team_id:
            return _update_team(event, user, team_id)
        elif method == "DELETE" and team_id:
            return _delete_team(event, user, team_id)
        else:
            return _response(404, {"error": "Not found"})
    except Exception as e:
        logger.exception("teams-service error")
        return _response(500, {"error": "Internal server error", "message": str(e)})


if __name__ == "__main__":
    print(handler({"httpMethod": "GET", "path": "/teams-service", "headers": {}}))
