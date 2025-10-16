import os, sys
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../trainer_manager"))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_trainer_crud():
    tid = "ash"
    payload = {"name": "Ash Ketchum", "email": "ash@test.local"}
    r = client.post(f"/trainer/{tid}", json=payload)
    assert r.status_code == 200
    r = client.get(f"/trainer/{tid}")
    assert r.status_code == 200
    assert r.json()["data"]["name"].startswith("Ash")
    r = client.delete(f"/trainer/{tid}")
    assert r.status_code == 200
    r = client.get(f"/trainer/{tid}")
    assert r.status_code == 404
