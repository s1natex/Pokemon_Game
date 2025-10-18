from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="frontend")

# for HPA tests
REQS = Counter("http_requests_total", "total http requests", ["path"])

@app.middleware("http")
async def count_requests(request, call_next):
    resp = await call_next(request)
    try:
        REQS.labels(request.url.path).inc()
    except Exception:
        pass
    return resp

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/")
def root():
    # body for root endpoint
    return {"service": "frontend", "message": "pokemon mvp(test7)"}

@app.get("/metrics")
def metrics():
    # expose prometheus metrics
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
