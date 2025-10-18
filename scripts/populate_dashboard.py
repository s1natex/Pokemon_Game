#!/usr/bin/env python3
import threading
import time
import urllib.request
import urllib.error
import json
import random
from collections import defaultdict

# prompt for base address
base = input("Enter the application base address (eg http://<alb-dns>/): ").strip()
if not base:
    print("no address provided")
    raise SystemExit(1)
if not base.endswith("/"):
    base += "/"

DURATION = 120
CONCURRENCY = 20
PROGRESS_INTERVAL = 5

ENDPOINTS_OK = [
    "",            # root
    "healthz",
    "metrics"
]

ENDPOINTS_CLIENT_ERROR = [
    "fetch",               # POST invalid payload to trigger 400
    "pokemon/0",           # invalid id to trigger 400
    "trainer/",            # malformed path to trigger 404 or 400
]

ENDPOINTS_NOT_FOUND = [
    "this-path-does-not-exist",
    "api/unknown"
]

stop_flag = False
counts = defaultdict(int)
lock = threading.Lock()

def do_get(path):
    url = base + path
    try:
        with urllib.request.urlopen(url, timeout=6) as r:
            code = r.getcode()
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = 0
    with lock:
        counts[code] += 1

def do_post(path, data):
    url = base + path
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            code = r.getcode()
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = 0
    with lock:
        counts[code] += 1

def worker():
    i = 0
    while not stop_flag:
        r = random.random()
        if r < 0.6:
            path = random.choice(ENDPOINTS_OK)
            do_get(path)
        elif r < 0.85:
            path = random.choice(ENDPOINTS_CLIENT_ERROR)
            if path == "fetch":
                payload = {"id": 0, "source": "stress"}
            elif path.startswith("pokemon"):
                payload = {"name": ""}
            else:
                payload = {}
            do_post(path, payload)
        else:
            path = random.choice(ENDPOINTS_NOT_FOUND)
            do_get(path)
        i += 1

def print_progress(elapsed, last_total):
    with lock:
        total = sum(counts.values())
        ok = counts.get(200, 0)
        c400 = counts.get(400, 0)
        c404 = counts.get(404, 0)
        c500 = counts.get(500, 0)
        other = total - ok - c400 - c404 - c500
    print(f"[{int(elapsed)}s] total {total} new {total - last_total} ok {ok} 400 {c400} 404 {c404} 500 {c500} other {other}")
    return total

def main():
    print("starting stress test")
    print(f"target {base}")
    print(f"duration {DURATION}s concurrency {CONCURRENCY}")
    threads = []
    for _ in range(CONCURRENCY):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    start = time.time()
    last_total = 0
    while True:
        time.sleep(PROGRESS_INTERVAL)
        elapsed = time.time() - start
        last_total = print_progress(elapsed, last_total)
        if elapsed >= DURATION:
            break

    global stop_flag
    stop_flag = True
    for t in threads:
        t.join(timeout=1)

    with lock:
        total = sum(counts.values())
        ok = counts.get(200, 0)
        c400 = counts.get(400, 0)
        c404 = counts.get(404, 0)
        c500 = counts.get(500, 0)
        other = total - ok - c400 - c404 - c500

    print("\nsummary")
    print(f"total requests {total}")
    print(f"200 ok {ok}")
    print(f"400 client error {c400}")
    print(f"404 not found {c404}")
    print(f"500 server error {c500}")
    print(f"other {other}")
    print("done test")

if __name__ == "__main__":
    main()
