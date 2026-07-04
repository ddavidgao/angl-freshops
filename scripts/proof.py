from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "bin" / "python"
UVICORN = ROOT / ".venv" / "bin" / "uvicorn"


def main() -> int:
    processes = []
    try:
        run(["docker", "compose", "up", "-d", "postgres", "redis"])
        run(["make", "build"])
        run(["make", "test"])
        run(["make", "seed"])
        run(["docker", "compose", "exec", "redis", "redis-cli", "FLUSHDB"])

        worker = subprocess.Popen([str(PYTHON), "-m", "app.worker"], cwd=ROOT)
        api = subprocess.Popen(
            [str(UVICORN), "app.server:app", "--host", "127.0.0.1", "--port", "8810"],
            cwd=ROOT,
        )
        processes.extend([worker, api])
        wait_for_api()
        result = submit_order()
        print(json.dumps(result, sort_keys=True))
        return 0
    finally:
        for proc in processes:
            proc.terminate()
        for proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


def run(command: list[str]) -> None:
    env = os.environ.copy()
    env["ANGL_REPO"] = env.get("ANGL_REPO", str((ROOT.parent / "angl").resolve()))
    env["ANGL_MODEL_PROVIDER"] = env.get("ANGL_MODEL_PROVIDER", "claude-code")
    env["ANGL_MODEL"] = env.get("ANGL_MODEL", "sonnet")
    env["ANGL_MODEL_TIMEOUT"] = env.get("ANGL_MODEL_TIMEOUT", "180")
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def wait_for_api() -> None:
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            request.urlopen("http://127.0.0.1:8810/", timeout=1).read()
            return
        except (OSError, error.URLError):
            time.sleep(0.25)
    raise RuntimeError("api did not become ready")


def submit_order() -> dict:
    order = {
        "customer": "Mia",
        "delivery_zone": "west",
        "items": [
            {"id": "milk", "qty": 2},
            {"id": "eggs", "qty": 1},
            {"id": "bread", "qty": 1},
        ],
        "pressure": {
            "max_cost": 12,
            "risk": 3,
            "delay": 2,
            "substitution_budget": 3,
            "batch_minutes": 9,
        },
    }
    req = request.Request(
        "http://127.0.0.1:8810/api/orders",
        data=json.dumps(order).encode(),
        headers={"content-type": "application/json"},
        method="POST",
    )
    created = json.loads(request.urlopen(req, timeout=5).read())
    deadline = time.time() + 20
    while time.time() < deadline:
        current = json.loads(
            request.urlopen(
                f"http://127.0.0.1:8810/api/orders/{created['order_id']}",
                timeout=5,
            ).read()
        )
        if current.get("promise"):
            expect(current["status"] == "promised", current)
            expect(current["promise"]["store"] == "north-market", current)
            expect(
                current["promise"]["courier_batch"] == ["drop-17", "drop-22"],
                current,
            )
            expect(current["promise"]["promised_minutes"] == 56, current)
            return current
        time.sleep(0.25)
    raise RuntimeError("promise was not produced")


def expect(condition: bool, value: object) -> None:
    if not condition:
        raise RuntimeError(f"unexpected proof result: {value!r}")


if __name__ == "__main__":
    raise SystemExit(main())
