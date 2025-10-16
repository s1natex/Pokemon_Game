from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="scheduler")

# critical metrics for visibility
REQS = Counter("scheduler_requests_total", "total http requests", ["path", "method"])
SCHEDULED = Counter("scheduler_jobs_total", "jobs accepted", ["type"])

class Job(BaseModel):
    type: str
    payload: dict | None = None

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

@app.post("/schedule")
def schedule(job: Job):
    # critical accept job for later dispatch
    if not job.type:
        raise HTTPException(status_code=400, detail="invalid")
    SCHEDULED.labels(job.type).inc()
    return {"status": "accepted", "type": job.type}
