"""
Members service Lambda handler.

Routes:
  POST   /members-service         — create a member
  GET    /members-service         — list members (optional ?search=&team_id=)
  GET    /members-service/{id}    — get member by id
  PUT    /members-service/{id}    — update member
  DELETE /members-service/{id}    — delete member
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


MEMBER_COLS = [
    "id", "name", "email", "team_id", "role",
    "is_team_leader", "is_direct_staff", "location",
    "created_at", "updated_at",
]


# ── Route handlers ──────────────────────────────────────────────────
def _create_member(event, user):
    if user["role"] not in WRITE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    data = _parse_body(event)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    if not name or not email:
        return _response(400, {"error": "name and email are required"})

    member_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM members WHERE email = %s", (email,))
            if cur.fetchone():
                conn.rollback()
                return _response(400, {"error": "Email already exists"})

            cur.execute(
                """INSERT INTO members
                   (id, name, email, team_id, role, is_team_leader, is_direct_staff, location, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    member_id, name, email,
                    data.get("team_id") or None,
                    data.get("role", "member"),
                    bool(data.get("is_team_leader", False)),
                    bool(data.get("is_direct_staff", True)),
                    data.get("location", ""),
                    now, now,
                ),
            )
        conn.commit()
        return _response(201, {"message": "Member created successfully", "id": member_id})
    except Exception:
        conn.rollback()
        raise


def _list_members(event, user):
    params = event.get("queryStringParameters") or {}
    search = params.get("search")
    team_id = params.get("team_id")

    conn = _get_conn()
    with conn.cursor() as cur:
        query = "SELECT " + ", ".join(MEMBER_COLS) + " FROM members WHERE 1=1"
        args = []
        if search:
            query += " AND (name ILIKE %s OR email ILIKE %s)"
            args += [f"%{search}%", f"%{search}%"]
        if team_id:
            query += " AND team_id = %s"
            args.append(team_id)
        query += " ORDER BY name"
        cur.execute(query, args)
        rows = cur.fetchall()

    members = [_row_to_dict(r, MEMBER_COLS) for r in rows]
    return _response(200, {"members": members})


def _get_member(event, user, member_id):
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT " + ", ".join(MEMBER_COLS) + " FROM members WHERE id = %s",
            (member_id,),
        )
        row = cur.fetchone()
    if not row:
        return _response(404, {"error": "Member not found"})
    return _response(200, _row_to_dict(row, MEMBER_COLS))


def _update_member(event, user, member_id):
    if user["role"] not in WRITE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    data = _parse_body(event)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM members WHERE id = %s", (member_id,))
            if not cur.fetchone():
                conn.rollback()
                return _response(404, {"error": "Member not found"})

            sets, args = [], []
            for field in ["name", "email", "team_id", "role", "location"]:
                if field in data and data[field] is not None:
                    sets.append(f"{field} = %s")
                    val = data[field].strip().lower() if field == "email" else data[field]
                    args.append(val)
            for field in ["is_team_leader", "is_direct_staff"]:
                if field in data:
                    sets.append(f"{field} = %s")
                    args.append(bool(data[field]))
            if sets:
                sets.append("updated_at = %s")
                args.append(datetime.now(timezone.utc))
                args.append(member_id)
                cur.execute(f"UPDATE members SET {', '.join(sets)} WHERE id = %s", args)
        conn.commit()
        return _response(200, {"message": "Member updated successfully"})
    except Exception:
        conn.rollback()
        raise


def _delete_member(event, user, member_id):
    if user["role"] not in DELETE_ROLES:
        return _response(403, {"error": "Insufficient permissions"})

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM members WHERE id = %s", (member_id,))
            if not cur.fetchone():
                conn.rollback()
                return _response(404, {"error": "Member not found"})
            cur.execute("DELETE FROM members WHERE id = %s", (member_id,))
        conn.commit()
        return _response(204, {})
    except Exception:
        conn.rollback()
        raise


# ── Lambda entry point ──────────────────────────────────────────────
def handler(event, context=None):
    logger.info("members-service event: %s", json.dumps(event, default=str))

    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("path") or event.get("rawPath") or ""

    if method == "OPTIONS":
        return _response(200, {})

    user = _authenticate(event)
    if not user:
        return _response(401, {"error": "Not authenticated"})

    try:
        member_id = _extract_id(path)

        if method == "POST" and not member_id:
            return _create_member(event, user)
        elif method == "GET" and not member_id:
            return _list_members(event, user)
        elif method == "GET" and member_id:
            return _get_member(event, user, member_id)
        elif method == "PUT" and member_id:
            return _update_member(event, user, member_id)
        elif method == "DELETE" and member_id:
            return _delete_member(event, user, member_id)
        else:
            return _response(404, {"error": "Not found"})
    except Exception as e:
        logger.exception("members-service error")
        return _response(500, {"error": "Internal server error", "message": str(e)})


if __name__ == "__main__":
    print(handler({"httpMethod": "GET", "path": "/members-service", "headers": {}}))
