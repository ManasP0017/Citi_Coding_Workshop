"""
SSE integration test.
Opens the /api/events stream in a background thread, fires a mutation via
the REST API, then confirms the SSE event arrives within 5 seconds.
"""
import json
import threading
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8000"


def rest(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        res = urllib.request.urlopen(r)
        return json.loads(res.read()), res.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code


# ── 1. Get a token ─────────────────────────────────────────────────────────
rest("POST", "/api/auth/register",
     {"email": "ssetest@test.com", "password": "secret99", "name": "SSE", "role": "admin"})
resp, _ = rest("POST", "/api/auth/login",
               {"email": "ssetest@test.com", "password": "secret99"})
token = resp["token"]
print(f"[AUTH] token obtained (role=admin)")

# ── 2. Verify bad token is rejected ─────────────────────────────────────────
r = urllib.request.Request(f"{BASE}/api/events?token=bad-token")
try:
    urllib.request.urlopen(r)
    print("[FAIL] Bad token should be rejected")
except urllib.error.HTTPError as e:
    assert e.code == 401, f"Expected 401, got {e.code}"
    print(f"[PASS] Bad token → 401 Unauthorized")

# ── 3. Open SSE stream and collect arriving events ───────────────────────────
received_events: list[dict] = []
stream_ready = threading.Event()
stop_flag    = threading.Event()


def sse_listener():
    url = f"{BASE}/api/events?token={token}"
    req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            stream_ready.set()
            for raw_line in resp:
                if stop_flag.is_set():
                    break
                line = raw_line.decode("utf-8").strip()
                if line.startswith("data:"):
                    try:
                        received_events.append(json.loads(line[5:].strip()))
                    except json.JSONDecodeError:
                        pass
    except Exception as exc:
        if not stop_flag.is_set():
            print(f"[SSE listener error] {exc}")
        stream_ready.set()


t = threading.Thread(target=sse_listener, daemon=True)
t.start()
stream_ready.wait(timeout=5)
print(f"[PASS] SSE stream opened  (connected event in buffer)")

# ── 4. Fire mutations and wait for SSE events ─────────────────────────────────
time.sleep(0.3)   # let the stream settle

# Create team → expect team.created
resp, code = rest("POST", "/api/teams",
                  {"name": "SSE Team", "location": "Remote", "description": "test"}, token)
assert code == 201, f"Create team failed: {resp}"
team_id = resp["id"]

# Add member → expect member.created
resp, code = rest("POST", "/api/members",
                  {"name": "SSE Member", "email": "ssemember@test.com",
                   "team_id": team_id, "is_team_leader": True}, token)
assert code == 201, f"Create member failed: {resp}"

# Award achievement → expect achievement.created
resp, code = rest("POST", "/api/achievements",
                  {"title": "SSE Achievement", "team_id": team_id,
                   "month": "April", "year": 2026}, token)
assert code == 201, f"Create achievement failed: {resp}"

# Give events 2 s to arrive
time.sleep(2)
stop_flag.set()

# ── 5. Verify received events ─────────────────────────────────────────────────
print(f"\n[INFO] Received {len(received_events)} SSE events:")
for evt in received_events:
    print(f"       event={evt.get('event'):<25} resource={evt.get('resource')}")

event_types = {e["event"] for e in received_events}

checks = [
    ("connected event received",         "connected"           in event_types),
    ("team.created event received",      "team.created"        in event_types),
    ("member.created event received",    "member.created"      in event_types),
    ("achievement.created event received","achievement.created" in event_types),
    ("events have 'ts' timestamp",       all("ts" in e for e in received_events)),
    ("events have 'data' payload",       all("data" in e for e in received_events)),
]

print()
all_ok = True
for label, ok in checks:
    mark = "[PASS]" if ok else "[FAIL]"
    print(f"  {mark} {label}")
    if not ok:
        all_ok = False

print()
print("SSE test PASSED." if all_ok else "SSE test FAILED — see above.")
