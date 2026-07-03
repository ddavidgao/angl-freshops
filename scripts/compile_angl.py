from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANGL_REPO = Path(os.environ.get("ANGL_REPO", ROOT.parent / "angl")).resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ANGL_REPO))

from angl.run import compile_until_green, load_program, topo_order  # noqa: E402
from angl.verify import verify_spec  # noqa: E402
from scripts.policy import apply_policy, write_decision_manifest  # noqa: E402


def main() -> int:
    target = ROOT / "specs" / "build_delivery_promise.angl"
    build_dir = ROOT / "build" / "latest"
    units = apply_policy(load_program(str(target)))
    failures = []
    for name in topo_order(units):
        spec = units[name]
        spec_path = ROOT / "specs" / f"{name}.angl"
        unit_build_dir = build_dir
        cached = _cached_green(spec, spec_path, unit_build_dir)
        if cached:
            print(f"{name}: cached {cached['passed']}/{cached['total']}", flush=True)
            continue
        build, result, attempts = compile_until_green(
            spec,
            str(unit_build_dir),
            units,
            max_attempts=int(os.environ.get("ANGL_MAX_ATTEMPTS", "3")),
        )
        print(
            f"{name}: {result['passed']}/{result['total']} in {attempts} attempt(s)",
            flush=True,
        )
        if result["passed"] != result["total"]:
            failures.append({"unit": name, "result": result, "build": build})
    if failures:
        print(json.dumps(failures, indent=2))
        return 1
    write_decision_manifest(build_dir, units)
    return 0


def _cached_green(spec, spec_path, build_dir):
    manifest_path = build_dir / f"{spec['func']}.manifest.json"
    if not manifest_path.exists():
        return None
    if manifest_path.stat().st_mtime < spec_path.stat().st_mtime:
        return None
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("target") != spec["target"]:
        return None
    build = {
        "implementation": str(build_dir / manifest["implementation"]),
        "judge_adapter": str(build_dir / manifest["judge_adapter"]),
        "shim": str(build_dir / manifest["judge_adapter"]),
        "target": spec["target"],
    }
    report = verify_spec(spec, build, timeout=60)
    if report["passed"] == report["total"]:
        return report
    return None


if __name__ == "__main__":
    raise SystemExit(main())
