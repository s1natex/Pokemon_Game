import time
import requests

BASE = {
    "frontend": "http://localhost:8080",
    "pokemon_manager": "http://localhost:8081",
    "scheduler": "http://localhost:8082",
    "pokemon_fetcher": "http://localhost:8083",
    "battle_manager": "http://localhost:8084",
    "trainer_manager": "http://localhost:8085",
}

def wait_ready(url, path="/healthz", tries=30, delay=1):
    # critical wait for service health
    for _ in range(tries):
        try:
            r = requests.get(f"{url}{path}", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False

def test_services_ready():
    for name, url in BASE.items():
        assert wait_ready(url), f"{name} not ready"

def test_trainer_crud_runtime():
    url = BASE["trainer_manager"]
    tid = "ash"
    payload = {"name": "Ash Ketchum", "email": "ash@test.local"}
    r = requests.post(f"{url}/trainer/{tid}", json=payload, timeout=3)
    assert r.status_code == 200
    r = requests.get(f"{url}/trainer/{tid}", timeout=3)
    assert r.status_code == 200
    r = requests.delete(f"{url}/trainer/{tid}", timeout=3)
    assert r.status_code == 200

def test_pokemon_upsert_get_runtime():
    url = BASE["pokemon_manager"]
    pid = "25"
    payload = {"name": "pikachu"}
    r = requests.post(f"{url}/pokemon/{pid}", json=payload, timeout=3)
    assert r.status_code == 200
    r = requests.get(f"{url}/pokemon/{pid}", timeout=3)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "pikachu"

def test_scheduler_accepts_job_runtime():
    url = BASE["scheduler"]
    r = requests.post(f"{url}/schedule", json={"type": "FETCH_POKEMON", "payload": {"id": 25}}, timeout=3)
    assert r.status_code == 200

def test_fetcher_accepts_job_runtime():
    url = BASE["pokemon_fetcher"]
    r = requests.post(f"{url}/fetch", json={"id": 25, "source": "runtime"}, timeout=3)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_battle_flow_runtime():
    url = BASE["battle_manager"]
    start = {"trainer_a": "ash", "trainer_b": "misty", "pokemon_a": 25, "pokemon_b": 120}
    r = requests.post(f"{url}/battle", json=start, timeout=3)
    assert r.status_code == 200
    bid = r.json()["battle_id"]
    r = requests.get(f"{url}/battle/{bid}", timeout=3)
    assert r.status_code == 200
    r = requests.post(f"{url}/battle/{bid}/move", json={"actor": "ash", "move": "tackle"}, timeout=3)
    assert r.status_code == 200
    r = requests.post(f"{url}/battle/{bid}/move", json={"actor": "misty", "move": "splash"}, timeout=3)
    assert r.status_code == 200
