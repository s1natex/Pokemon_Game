import os, sys
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../battle_manager"))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_battle_flow():
    start = {
        "trainer_a": "ash",
        "trainer_b": "misty",
        "pokemon_a": 25,
        "pokemon_b": 120
    }
    r = client.post("/battle", json=start)
    assert r.status_code == 200
    bid = r.json()["battle_id"]

    r = client.get(f"/battle/{bid}")
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"

    r = client.post(f"/battle/{bid}/move", json={"actor":"ash","move":"tackle"})
    assert r.status_code == 200
    assert r.json()["status"] in ("in_progress","finished")

    r = client.post(f"/battle/{bid}/move", json={"actor":"misty","move":"splash"})
    assert r.status_code == 200
    assert r.json()["status"] == "finished"
