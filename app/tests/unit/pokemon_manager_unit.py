import os, sys
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../pokemon_manager"))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from main import app  # noqa
from fastapi.testclient import TestClient

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_upsert_get_delete():
    pid = "25"
    payload = {"name": "pikachu"}
    r = client.post(f"/pokemon/{pid}", json=payload)
    assert r.status_code == 200
    r = client.get(f"/pokemon/{pid}")
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "pikachu"
    r = client.delete(f"/pokemon/{pid}")
    assert r.status_code == 200
    r = client.get(f"/pokemon/{pid}")
    assert r.status_code == 404
