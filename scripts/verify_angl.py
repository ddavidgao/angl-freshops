from __future__ import annotations

import os
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANGL_REPO = Path(os.environ.get("ANGL_REPO", ROOT.parent / "angl")).resolve()
sys.path.insert(0, str(ANGL_REPO))

from angl.parse import parse  # noqa: E402
from angl.verify import verify_spec  # noqa: E402


def main() -> int:
    build_dir = ROOT / "build" / "latest"
    failed = 0
    for path in sorted((ROOT / "specs").glob("*.angl")):
        spec = parse(path.read_text())
        manifest_path = build_dir / f"{spec['func']}.manifest.json"
        manifest = json.loads(manifest_path.read_text())
        build = {
            "implementation": str(build_dir / manifest["implementation"]),
            "judge_adapter": str(build_dir / manifest["judge_adapter"]),
            "shim": str(build_dir / manifest["judge_adapter"]),
            "target": spec["target"],
        }
        report = verify_spec(spec, build, timeout=60)
        print(f"{spec['name']}: {report['passed']}/{report['total']}")
        failed += report["passed"] != report["total"]
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
