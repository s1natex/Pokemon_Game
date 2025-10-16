import os, sys
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../pokemon_fetcher"))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_fetch_valid():
    payload = {"id": 25, "source": "test"}
    r = client.post("/fetch", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["id"] == 25

def test_fetch_invalid_id():
    payload = {"id": 0}
    r = client.post("/fetch", json=payload)
    assert r.status_code == 400
