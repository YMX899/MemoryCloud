from __future__ import annotations

import argparse
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def hit(url: str, path: str, timeout: float) -> tuple[bool, float, str]:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}{path}", timeout=timeout) as response:
            response.read(1024)
            return 200 <= response.status < 500, time.perf_counter() - start, str(response.status)
    except urllib.error.HTTPError as exc:
        return exc.code < 500, time.perf_counter() - start, str(exc.code)
    except Exception as exc:
        return False, time.perf_counter() - start, exc.__class__.__name__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--concurrency", type=int, default=1000)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    paths = ["/health", "/api/catalog", "/api/protocol/schema"]
    started = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(hit, args.url, paths[i % len(paths)], args.timeout)
            for i in range(args.requests)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - started
    ok = [item for item in results if item[0]]
    latencies = [item[1] for item in results]
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
    summary = {
        "requests": args.requests,
        "concurrency": args.concurrency,
        "ok": len(ok),
        "failed": len(results) - len(ok),
        "elapsed_seconds": round(elapsed, 3),
        "rps": round(args.requests / elapsed, 2),
        "p95_ms": round(p95 * 1000, 2),
    }
    print(summary)
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
