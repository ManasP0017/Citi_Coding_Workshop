"""
Insights service Lambda handler.

Routes:
  GET /insights-service — return organisational analytics metrics
"""

import json
import logging
import os
from datetime import datetime

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
        _conn.autocommit = True
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


def _get_insights():
    """
    Answers the 6 business questions using parameterized SQL.
    All queries run in a single connection with read-only semantics.
    """
    conn = _get_conn()
    with conn.cursor() as cur:
        # Total teams
        cur.execute("SELECT COUNT(*) FROM teams")
        total_teams = cur.fetchone()[0]

        # Total members
        cur.execute("SELECT COUNT(*) FROM members")
        total_members = cur.fetchone()[0]

        # Teams where leader is not co-located with at least one other member
        cur.execute("""
            SELECT COUNT(DISTINCT t.id)
            FROM teams t
            JOIN members leader ON leader.team_id = t.id AND leader.is_team_leader = TRUE
            JOIN members other  ON other.team_id = t.id AND other.is_team_leader = FALSE
            WHERE other.location IS NOT NULL
              AND other.location != ''
              AND other.location != leader.location
        """)
        teams_with_leader_not_colocated = cur.fetchone()[0]

        # Teams where the leader is non-direct staff
        cur.execute("""
            SELECT COUNT(DISTINCT t.id)
            FROM teams t
            JOIN members m ON m.team_id = t.id
                          AND m.is_team_leader = TRUE
                          AND m.is_direct_staff = FALSE
        """)
        teams_with_nondir_leader = cur.fetchone()[0]

        # Teams where non-direct staff ratio exceeds 20%
        cur.execute("""
            SELECT COUNT(*) FROM (
                SELECT m.team_id,
                       COUNT(*) AS total,
                       SUM(CASE WHEN m.is_direct_staff = FALSE THEN 1 ELSE 0 END) AS nondir
                FROM members m
                WHERE m.team_id IS NOT NULL
                GROUP BY m.team_id
                HAVING SUM(CASE WHEN m.is_direct_staff = FALSE THEN 1 ELSE 0 END)::float
                       / COUNT(*) > 0.20
            ) sub
        """)
        teams_nondir_ratio_above_20 = cur.fetchone()[0]

        # Teams that report to an organisation leader
        cur.execute("""
            SELECT COUNT(*) FROM teams
            WHERE organization_leader_id IS NOT NULL
              AND organization_leader_id != ''
        """)
        teams_reporting_to_org_leader = cur.fetchone()[0]

    return {
        "total_teams": total_teams,
        "total_members": total_members,
        "teams_with_leader_not_colocated": teams_with_leader_not_colocated,
        "teams_with_nondir_leader": teams_with_nondir_leader,
        "teams_nondir_ratio_above_20": teams_nondir_ratio_above_20,
        "teams_reporting_to_org_leader": teams_reporting_to_org_leader,
    }


# ── Lambda entry point ──────────────────────────────────────────────
def handler(event, context=None):
    logger.info("insights-service event: %s", json.dumps(event, default=str))

    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")

    if method == "OPTIONS":
        return _response(200, {})

    user = _authenticate(event)
    if not user:
        return _response(401, {"error": "Not authenticated"})

    try:
        if method == "GET":
            return _response(200, _get_insights())
        else:
            return _response(404, {"error": "Not found"})
    except Exception as e:
        logger.exception("insights-service error")
        return _response(500, {"error": "Internal server error", "message": str(e)})


if __name__ == "__main__":
    print(handler({"httpMethod": "GET", "path": "/insights-service", "headers": {}}))
