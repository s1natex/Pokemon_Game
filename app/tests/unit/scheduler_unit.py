import os, sys
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scheduler"))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_schedule_accepts_job():
    payload = {"type": "FETCH_POKEMON", "payload": {"id": 25}}
    r = client.post("/schedule", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "accepted"
    assert body["type"] == "FETCH_POKEMON"
