"""
Auth service Lambda handler.

Routes:
  POST /auth-service/register  — create a new user
  POST /auth-service/login     — authenticate and return JWT
  GET  /auth-service/me        — return current user info from JWT
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── Config ──────────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "changeme-super-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8

PG_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASS", "postgres123"),
    "dbname": os.getenv("POSTGRES_NAME", "postgres"),
    "connect_timeout": 15,
}

VALID_ROLES = {"admin", "manager", "contributor", "viewer"}
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
}

# ── Connection pooling across Lambda invocations ────────────────────
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
            CREATE TABLE IF NOT EXISTS users (
                id         VARCHAR(36) PRIMARY KEY,
                email      VARCHAR(255) UNIQUE NOT NULL,
                password   VARCHAR(255) NOT NULL,
                name       VARCHAR(255) NOT NULL,
                role       VARCHAR(50) NOT NULL DEFAULT 'viewer',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
    conn.commit()


# ── Helpers ─────────────────────────────────────────────────────────
def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body)}


def _hash_password(plain):
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _create_token(user_id, email, role):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def _get_bearer_token(event):
    headers = event.get("headers") or {}
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def _parse_body(event):
    body = event.get("body", "{}")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body or {}


# ── Route handlers ──────────────────────────────────────────────────
def _register(event):
    data = _parse_body(event)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    role = data.get("role", "viewer")

    if not email or not password or not name:
        return _response(400, {"error": "email, password, and name are required"})
    if role not in VALID_ROLES:
        return _response(400, {"error": f"Invalid role. Must be one of: {sorted(VALID_ROLES)}"})

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                conn.rollback()
                return _response(400, {"error": "Email already registered"})

            user_id = str(uuid.uuid4())
            cur.execute(
                """INSERT INTO users (id, email, password, name, role)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, email, _hash_password(password), name, role),
            )
        conn.commit()
        return _response(201, {"message": "User registered successfully", "id": user_id})
    except Exception:
        conn.rollback()
        raise


def _login(event):
    data = _parse_body(event)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return _response(400, {"error": "email and password are required"})

    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, email, password, name, role FROM users WHERE email = %s",
            (email,),
        )
        row = cur.fetchone()

    if not row or not _verify_password(password, row[2]):
        return _response(401, {"error": "Invalid email or password"})

    token = _create_token(row[0], row[1], row[4])
    return _response(200, {"token": token})


def _me(event):
    token = _get_bearer_token(event)
    if not token:
        return _response(401, {"error": "Not authenticated"})

    try:
        payload = _decode_token(token)
    except jwt.ExpiredSignatureError:
        return _response(401, {"error": "Token has expired"})
    except jwt.InvalidTokenError:
        return _response(401, {"error": "Invalid token"})

    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, email, name, role FROM users WHERE id = %s",
            (payload["user_id"],),
        )
        row = cur.fetchone()

    if not row:
        return _response(401, {"error": "User not found"})

    return _response(200, {"id": row[0], "email": row[1], "name": row[2], "role": row[3]})


# ── Lambda entry point ──────────────────────────────────────────────
def handler(event, context=None):
    logger.info("auth-service event: %s", json.dumps(event, default=str))

    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("path") or event.get("rawPath") or ""

    # Handle CORS preflight
    if method == "OPTIONS":
        return _response(200, {})

    try:
        if method == "POST" and path.endswith("/register"):
            return _register(event)
        elif method == "POST" and path.endswith("/login"):
            return _login(event)
        elif method == "GET" and path.endswith("/me"):
            return _me(event)
        else:
            return _response(404, {"error": "Not found"})
    except Exception as e:
        logger.exception("auth-service error")
        return _response(500, {"error": "Internal server error", "message": str(e)})


if __name__ == "__main__":
    print(handler({"httpMethod": "GET", "path": "/me", "headers": {}}))
