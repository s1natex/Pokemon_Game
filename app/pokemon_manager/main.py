from fastapi import FastAPI, HTTPException, Response
from prometheus_client import Counter, Summary, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="pokemon-manager")

# metrics for visibility
REQS = Counter("pokemon_requests_total", "total http requests", ["path", "method"])
LAT  = Summary("pokemon_request_seconds", "request latency seconds")

# in memory db
POKE = {}

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

@app.get("/pokemon/{pid}")
def get_pokemon(pid: str):
    # critical no data handling
    if pid not in POKE:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": pid, "data": POKE[pid]}

@app.post("/pokemon/{pid}")
def upsert_pokemon(pid: str, body: dict):
    # critical write path
    POKE[pid] = body
    return {"status": "ok", "id": pid}

@app.delete("/pokemon/{pid}")
def delete_pokemon(pid: str):
    # critical delete path
    if pid in POKE:
        del POKE[pid]
    return {"status": "ok"}
