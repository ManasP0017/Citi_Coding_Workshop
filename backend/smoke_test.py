"""Quick smoke test covering all modules and RBAC rules."""
import urllib.request, urllib.error, json, time

RUN = str(int(time.time()))[-5:]   # unique suffix per run

BASE = "http://localhost:8000"

def req(method, path, body=None, token=None):
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

failures = []

def check(label, cond, detail=""):
    if cond:
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label} — {detail}")
        failures.append(label)

# ── Health ─────────────────────────────────────────────────────────────────
resp, code = req("GET", "/health")
check("GET /health", code == 200 and resp.get("status") == "ok")

resp, code = req("GET", "/health/db")
check("GET /health/db", code == 200 and resp.get("db") == "connected")

# ── Auth ───────────────────────────────────────────────────────────────────
req("POST", "/api/auth/register",
    {"email": f"archtest{RUN}@test.com", "password": "secret99", "name": "Admin", "role": "admin"})
resp, code = req("POST", "/api/auth/login",
                 {"email": f"archtest{RUN}@test.com", "password": "secret99"})
check("POST /api/auth/login", code == 200 and "token" in resp)
token = resp.get("token", "")

resp, code = req("GET", "/api/auth/me", token=token)
check("GET /api/auth/me", code == 200 and resp.get("role") == "admin", resp)

# ── Teams ──────────────────────────────────────────────────────────────────
resp, code = req("POST", "/api/teams",
                 {"name": "Arch Team", "location": "NYC", "description": "test"}, token)
check("POST /api/teams", code == 201, resp)
team_id = resp.get("id", "")

resp, code = req("GET", "/api/teams", token=token)
check("GET /api/teams", code == 200 and len(resp.get("teams", [])) >= 1)

resp, code = req("GET", f"/api/teams/{team_id}", token=token)
check("GET /api/teams/:id", code == 200)

resp, code = req("PUT", f"/api/teams/{team_id}", {"description": "updated"}, token)
check("PUT /api/teams/:id", code == 200)

# ── Members ────────────────────────────────────────────────────────────────
resp, code = req("POST", "/api/members",
                 {"name": "Charlie", "email": f"charlie_arch{RUN}@test.com",
                  "team_id": team_id, "is_team_leader": True, "location": "NYC"}, token)
check("POST /api/members", code == 201, resp)
member_id = resp.get("id", "")

resp, code = req("GET", f"/api/members?team_id={team_id}", token=token)
check("GET /api/members?team_id=...", code == 200)

resp, code = req("PUT", f"/api/members/{member_id}", {"location": "LA"}, token)
check("PUT /api/members/:id", code == 200)

# ── Achievements ───────────────────────────────────────────────────────────
resp, code = req("POST", "/api/achievements",
                 {"title": "Q1 Launch", "team_id": team_id, "month": "March", "year": 2026}, token)
check("POST /api/achievements", code == 201, resp)
ach_id = resp.get("id", "")

resp, code = req("GET", "/api/achievements", token=token)
check("GET /api/achievements", code == 200)

resp, code = req("PUT", f"/api/achievements/{ach_id}", {"title": "Updated"}, token)
check("PUT /api/achievements/:id", code == 200)

# ── Insights ───────────────────────────────────────────────────────────────
resp, code = req("GET", "/api/insights", token=token)
check("GET /api/insights", code == 200 and "total_teams" in resp, resp)

# ── RBAC: Viewer ───────────────────────────────────────────────────────────
req("POST", "/api/auth/register",
    {"email": f"viewer_arch{RUN}@test.com", "password": "secret99", "name": "V", "role": "viewer"})
vresp, _ = req("POST", "/api/auth/login",
               {"email": f"viewer_arch{RUN}@test.com", "password": "secret99"})
vtoken = vresp.get("token", "")

resp, code = req("POST", "/api/teams", {"name": "X"}, vtoken)
check("Viewer blocked from POST /api/teams", code == 403, f"got {code}")

resp, code = req("GET", "/api/teams", token=vtoken)
check("Viewer allowed GET /api/teams", code == 200)

resp, code = req("DELETE", f"/api/members/{member_id}", token=vtoken)
check("Viewer blocked from DELETE", code == 403, f"got {code}")

# ── RBAC: Contributor ──────────────────────────────────────────────────────
req("POST", "/api/auth/register",
    {"email": f"contrib_arch{RUN}@test.com", "password": "secret99", "name": "C", "role": "contributor"})
cresp, _ = req("POST", "/api/auth/login",
               {"email": f"contrib_arch{RUN}@test.com", "password": "secret99"})
ctoken = cresp.get("token", "")

resp, code = req("POST", "/api/members",
                 {"name": "Dave", "email": f"dave_arch{RUN}@test.com"}, ctoken)
check("Contributor allowed POST /api/members", code == 201, resp)

resp, code = req("DELETE", f"/api/teams/{team_id}", token=ctoken)
check("Contributor blocked from DELETE /api/teams", code == 403, f"got {code}")

# ── Validation ─────────────────────────────────────────────────────────────
resp, code = req("POST", "/api/auth/register",
                 {"email": "bad-email", "password": "x", "name": "", "role": "admin"})
check("Invalid register rejected (422)", code == 422, resp)

resp, code = req("POST", "/api/achievements",
                 {"title": "T", "team_id": team_id, "month": "Octember", "year": 1999}, token)
check("Invalid month/year rejected (422)", code == 422, resp)

# ── Summary ────────────────────────────────────────────────────────────────
print()
if failures:
    print(f"FAILED ({len(failures)}):", failures)
else:
    print(f"All {22} checks passed.")
