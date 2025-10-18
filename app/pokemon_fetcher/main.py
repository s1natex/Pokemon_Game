from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="pokemon-fetcher")

# critical metrics only
REQS = Counter("fetcher_requests_total", "total http requests", ["path", "method"])
FETCHED = Counter("pokemon_fetched_total", "fetched events", ["source"])

class FetchJob(BaseModel):
    id: int
    source: str = "manual"

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

@app.post("/fetch")
def fetch(job: FetchJob):
    # critical validate id
    if job.id <= 0:
        raise HTTPException(status_code=400, detail="invalid id")
    # critical record event
    FETCHED.labels(job.source).inc()
    # simulated payload
    return {"status": "ok", "id": job.id, "name": "unknown"}

# (test)
