#!/usr/bin/env python3
"""
populate_dashboard.py
- Generates traffic to your frontend/ALB so CloudWatch dashboard panels show data.
- Prompts for the few values that vary per deployment.
- Sends a mix of healthy requests (e.g., /healthz) and "bad" ones (unknown paths or invalid POST) to surface 5xx/4xx and error logs.

Usage:
  python populate_dashboard.py
  # (or non-interactive)
  FRONTEND_BASE_URL=http://your-alb-dns python populate_dashboard.py --rps 5 --minutes 3 --invalid-ratio 0.3 --paths "/,/healthz,/api/pokemon,/api/trainers" --error-paths "/boom"
"""

import os
import sys
import time
import random
import threading
import argparse
from datetime import datetime, timedelta
from urllib.parse import urljoin
try:
    import requests
except ImportError:
    print("This script needs the 'requests' library. Install with: pip install requests")
    sys.exit(1)


def prompt(label, default=None):
    env_val = os.environ.get(label)
    if env_val:
        return env_val
    if default is None:
        val = input(f"{label}: ").strip()
        return val
    val = input(f"{label} [{default}]: ").strip()
    return val or default


def normalized_paths(s):
    if not s:
        return []
    parts = [p.strip() for p in s.split(",")]
    out = []
    for p in parts:
        if not p:
            continue
        if not p.startswith("/"):
            p = "/" + p
        out.append(p)
    return out


def choose_endpoint(valid_paths, invalid_ratio, error_paths):
    r = random.random()
    # Prefer explicit error paths if provided (attempt to trigger 5xx)
    if error_paths and r < invalid_ratio / 2:
        return random.choice(error_paths), "error"
    # Otherwise, decide invalid vs valid
    if r < invalid_ratio:
        # invalid path guaranteed to not exist
        return f"/does-not-exist-{random.randint(1000, 9999)}", "invalid"
    # healthy/normal path
    return random.choice(valid_paths), "valid"


def worker(stop_at, base_url, session, rps, valid_paths, invalid_ratio, error_paths, do_post_invalid):
    # even spacing for this thread roughly ~ 1 request per second if rps=1
    # if multiple threads, each handles a slice of the total RPS
    delay = 1.0 / max(rps, 0.0001)
    while time.time() < stop_at:
        path, kind = choose_endpoint(valid_paths, invalid_ratio, error_paths)
        url = urljoin(base_url, path.lstrip("/"))
        try:
            if do_post_invalid and (kind in ("invalid", "error") or path.startswith("/api/")):
                resp = session.post(url, data="invalid-json", headers={"Content-Type": "application/json"}, timeout=2)
            else:
                resp = session.get(url, timeout=2)
            code = resp.status_code
            # Light console output, but don’t spam
            if code >= 500:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 5xx from {path} -> {code}")
        except requests.RequestException as e:
            # Network/timeout — still useful to show errors in dashboard/alb metrics
            print(f"[{datetime.now().strftime('%H:%M:%S')}] request error to {path}: {e}")
        # pace
        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="Populate CloudWatch dashboard with frontend traffic.")
    parser.add_argument("--rps", type=float, default=None, help="Requests per second (total).")
    parser.add_argument("--minutes", type=float, default=None, help="How long to run (minutes).")
    parser.add_argument("--invalid-ratio", type=float, default=None, help="Fraction of traffic that is invalid/error-ish (0.0 - 1.0).")
    parser.add_argument("--paths", type=str, default=None, help='Comma-separated valid paths to hit (e.g. "/,/healthz,/api/pokemon").')
    parser.add_argument("--error-paths", type=str, default=None, help='Comma-separated paths that intentionally 500 if your app supports them (e.g. "/boom").')
    parser.add_argument("--threads", type=int, default=None, help="Number of worker threads (default scales from RPS).")
    parser.add_argument("--post-invalid", action="store_true", help="Send invalid POST to paths (helps surface errors in APIs).")
    parser.add_argument("--no-post-invalid", dest="post_invalid", action="store_false")
    parser.set_defaults(post_invalid=None)

    args = parser.parse_args()

    # Interactive prompts (with sane defaults) — overridden by CLI args or env
    base_url = os.environ.get("FRONTEND_BASE_URL") or prompt("FRONTEND_BASE_URL (e.g. http://k8s-xxx.elb.amazonaws.com)")
    if not base_url.startswith("http"):
        base_url = "http://" + base_url

    rps = args.rps if args.rps is not None else float(prompt("RPS (requests per second)", "5"))
    minutes = args.minutes if args.minutes is not None else float(prompt("DURATION_MINUTES", "3"))
    invalid_ratio = args.invalid_ratio if args.invalid_ratio is not None else float(prompt("INVALID_RATIO (0.0-1.0)", "0.25"))
    paths_input = args.paths if args.paths is not None else prompt("VALID_PATHS (comma-separated)", "/,/healthz,/api/pokemon,/api/trainers")
    error_paths_input = args.error_paths if args.error_paths is not None else prompt("ERROR_PATHS (comma-separated, optional)", "")
    post_invalid = args.post_invalid if args.post_invalid is not None else (prompt("POST_INVALID (y/n)", "y").lower() == "y")

    valid_paths = normalized_paths(paths_input)
    if not valid_paths:
        print("No valid paths provided; using '/'")
        valid_paths = ["/"]
    error_paths = normalized_paths(error_paths_input)

    # Threading plan
    threads = args.threads if args.threads is not None else max(1, min(16, int(rps)))  # cap lightly
    rps_per_thread = max(rps / threads, 0.1)

    print("\n=== Traffic Plan ===")
    print(f"Base URL       : {base_url}")
    print(f"RPS (total)    : {rps:.2f}  -> {threads} thread(s) ~ {rps_per_thread:.2f} rps each")
    print(f"Duration       : {minutes} minute(s)")
    print(f"Valid paths    : {', '.join(valid_paths)}")
    print(f"Invalid ratio  : {invalid_ratio:.2f} (fraction of requests)")
    print(f"Error paths    : {', '.join(error_paths) if error_paths else '(none)'}")
    print(f"POST invalid   : {'yes' if post_invalid else 'no'}")
    print("Starting in 2s… Ctrl+C to stop early.\n")
    time.sleep(2)

    stop_at = time.time() + minutes * 60
    sessions = [requests.Session() for _ in range(threads)]
    workers = []
    for i in range(threads):
        t = threading.Thread(
            target=worker,
            args=(stop_at, base_url, sessions[i], rps_per_thread, valid_paths, invalid_ratio, error_paths, post_invalid),
            daemon=True
        )
        t.start()
        workers.append(t)

    try:
        for t in workers:
            while t.is_alive():
                t.join(timeout=0.5)
    except KeyboardInterrupt:
        print("\nStopping… (waiting for threads to exit)")
    print("Done. Check your CloudWatch dashboard (Last 15 minutes).")


if __name__ == "__main__":
    main()
