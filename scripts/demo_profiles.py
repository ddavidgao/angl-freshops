from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNITS = [
    "normalize_order",
    "choose_fulfillment_store",
    "choose_substitution_pack",
    "choose_courier_batch",
    "compute_promise_minutes",
    "build_delivery_promise",
]


def main() -> int:
    assert_no_language_targets()
    standard = profile_targets("standard")
    native = profile_targets("native")
    print_profile("standard", standard)
    print_profile("native", native)
    print("\nSame Angl source. Different compiler profile.", flush=True)
    print("-------------------", flush=True)
    for name in UNITS:
        left = standard[name]
        right = native[name]
        marker = "==" if left == right else "->"
        print(f"{name:28} {left:8} {marker} {right}", flush=True)
    print("\nAssembly proof snapshot:", flush=True)
    print("  proof/assembly/compute_promise_minutes.s", flush=True)
    print("\nRuntime proof command:", flush=True)
    print("  ANGL_MODEL_PROVIDER=claude-code ANGL_MODEL=sonnet make proof PROFILE=native", flush=True)
    return 0


def assert_no_language_targets() -> None:
    offenders = []
    for path in sorted((ROOT / "specs").glob("*.angl")):
        if "Runs as:" in path.read_text():
            offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        raise RuntimeError(f"Angl specs still contain language targets: {offenders}")
    print("Angl source contains no language target hints.", flush=True)


def profile_targets(name: str) -> dict:
    data = json.loads((ROOT / "profiles" / f"{name}.json").read_text())
    selected = {unit: "python" for unit in UNITS}
    selected.update(data.get("targets", {}))
    return selected


def print_profile(name: str, targets: dict) -> None:
    print(f"\nprofiles/{name}.json", flush=True)
    for unit in UNITS:
        print(f"  {unit:28} {targets[unit]}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
