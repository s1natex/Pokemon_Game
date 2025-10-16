import os, sys
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("service") == "frontend"