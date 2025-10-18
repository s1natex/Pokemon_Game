from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="trainer-manager")

# critical metrics only
REQS = Counter("trainer_requests_total", "total http requests", ["path", "method"])
CREATED = Counter("trainer_created_total", "trainers created")

# in memory store
TRAINERS: dict[str, dict] = {}

class Trainer(BaseModel):
    name: str
    email: str | None = None

@app.middleware("http")
async def observe(request, call_next):
    REQS.labels(request.url.path, request.method).inc()
    resp = await call_next(request)
    return resp

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/trainer/{tid}")
def get_trainer(tid: str):
    t = TRAINERS.get(tid)
    if not t:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": tid, "data": t}

@app.post("/trainer/{tid}")
def upsert_trainer(tid: str, body: Trainer):
    TRAINERS[tid] = body.model_dump()
    CREATED.inc()
    return {"status": "ok", "id": tid}

@app.delete("/trainer/{tid}")
def delete_trainer(tid: str):
    if tid in TRAINERS:
        del TRAINERS[tid]
    return {"status": "ok"}

# (test7)
