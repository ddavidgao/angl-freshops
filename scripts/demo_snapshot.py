from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "latest"
SNAPSHOT = ROOT / "build" / "demo-before"


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"save", "diff"}:
        print("usage: python scripts/demo_snapshot.py save|diff")
        return 2
    if sys.argv[1] == "save":
        return save()
    return diff()


def save() -> int:
    if not BUILD.exists():
        print("build/latest does not exist")
        return 1
    if SNAPSHOT.exists():
        shutil.rmtree(SNAPSHOT)
    shutil.copytree(BUILD, SNAPSHOT)
    print(f"saved generated baseline: {SNAPSHOT}")
    return 0


def diff() -> int:
    if not SNAPSHOT.exists():
        print("missing build/demo-before; run save first")
        return 1
    changed = []
    for current in sorted(BUILD.glob("*.py")):
        before = SNAPSHOT / current.name
        if not before.exists() or digest(before) != digest(current):
            changed.append(current.name)
    if not changed:
        print("generated implementation changes: none")
        return 0
    print("generated implementation changes:")
    for name in changed:
        print(f"  {name}")
    return 0


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
