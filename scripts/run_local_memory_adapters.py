from __future__ import annotations

import signal
import os
import subprocess
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.memory_local_deployment import LOCAL_DEPLOYMENT_SPECS  # noqa: E402

PYTHON = BASE_DIR / ".venv" / "bin" / "python"
ADAPTER = BASE_DIR / "deployments" / "memory-systems" / "adapters" / "amp_local_memory_runtime.py"
DATA_DIR = Path(os.getenv("AMP_LOCAL_MEMORY_DATA_DIR", ".memorycloud-data/local-memory")).expanduser()


running = True


def handle_stop(signum, frame) -> None:
    global running
    running = False


def start_process(integration_id: str, port: int) -> subprocess.Popen:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["AMP_MEMORY_SYSTEM"] = integration_id
    env["AMP_MEMORY_RUNTIME_MODE"] = "amp_local_memory_runtime"
    env["AMP_LOCAL_MEMORY_DB"] = str(DATA_DIR / f"{integration_id}.sqlite3")
    return subprocess.Popen(
        [
            str(PYTHON),
            str(ADAPTER),
            "--system",
            integration_id,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--db",
            str(DATA_DIR / f"{integration_id}.sqlite3"),
        ],
        cwd=str(BASE_DIR),
        env=env,
    )


def main() -> int:
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)
    processes: dict[str, subprocess.Popen] = {}
    for integration_id, spec in sorted(LOCAL_DEPLOYMENT_SPECS.items(), key=lambda item: item[1]["startup_order"]):
        processes[integration_id] = start_process(integration_id, int(spec["port"]))
    try:
        while running:
            for integration_id, process in list(processes.items()):
                if process.poll() is not None and running:
                    time.sleep(0.2)
                    processes[integration_id] = start_process(integration_id, int(LOCAL_DEPLOYMENT_SPECS[integration_id]["port"]))
            time.sleep(1.0)
    finally:
        for process in processes.values():
            if process.poll() is None:
                process.terminate()
        deadline = time.time() + 8
        for process in processes.values():
            if process.poll() is None:
                timeout = max(0.1, deadline - time.time())
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
