from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Summary, generate_latest, CONTENT_TYPE_LATEST
import uuid

app = FastAPI(title="battle-manager")

# critical metrics only
REQS = Counter("battle_requests_total", "total http requests", ["path", "method"])
LAT = Summary("battle_request_seconds", "request latency seconds")
STARTED = Counter("battles_started_total", "battles started")
MOVES = Counter("battle_moves_total", "moves taken")

# in memory store
BATTLES: dict[str, dict] = {}

class StartBattle(BaseModel):
    trainer_a: str
    trainer_b: str
    pokemon_a: int
    pokemon_b: int

class Move(BaseModel):
    actor: str
    move: str

@app.middleware("http")
async def observe(request, call_next):
    REQS.labels(request.url.path, request.method).inc()
    with LAT.time():
        resp = await call_next(request)
    return resp

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/battle")
def start_battle(req: StartBattle):
    # critical validate trainers and pokemon ids
    if not req.trainer_a or not req.trainer_b or req.pokemon_a <= 0 or req.pokemon_b <= 0:
        raise HTTPException(status_code=400, detail="invalid")
    bid = str(uuid.uuid4())
    BATTLES[bid] = {
        "id": bid,
        "trainer_a": req.trainer_a,
        "trainer_b": req.trainer_b,
        "pokemon_a": req.pokemon_a,
        "pokemon_b": req.pokemon_b,
        "turn": req.trainer_a,
        "status": "in_progress",
        "log": [],
    }
    STARTED.inc()
    return {"battle_id": bid, "status": "in_progress"}

@app.get("/battle/{bid}")
def get_battle(bid: str):
    # critical ensure exists
    b = BATTLES.get(bid)
    if not b:
        raise HTTPException(status_code=404, detail="not found")
    return b

@app.post("/battle/{bid}/move")
def take_move(bid: str, m: Move):
    # critical ensure exists and active
    b = BATTLES.get(bid)
    if not b:
        raise HTTPException(status_code=404, detail="not found")
    if b["status"] != "in_progress":
        raise HTTPException(status_code=409, detail="finished")
    # critical basic turn check
    if m.actor != b["turn"]:
        raise HTTPException(status_code=409, detail="not your turn")
    # simulate turn flip
    b["log"].append({"actor": m.actor, "move": m.move})
    b["turn"] = b["trainer_b"] if b["turn"] == b["trainer_a"] else b["trainer_a"]
    if len(b["log"]) >= 2:
        b["status"] = "finished"
    MOVES.inc()
    return {"status": b["status"], "next_turn": b["turn"]}
