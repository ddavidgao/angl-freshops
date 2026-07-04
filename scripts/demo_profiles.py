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
    standard = load_profile("standard")
    scaleup = load_profile("scaleup")
    print_profile("standard", selected_targets(standard))
    print_profile("scaleup", selected_targets(scaleup))
    print("\nSame Angl source. Different compiler profile.", flush=True)
    print("-------------------", flush=True)
    for name in UNITS:
        left = selected_targets(standard)[name]
        right = selected_targets(scaleup)[name]
        marker = "==" if left == right else "->"
        print(f"{name:28} {left:8} {marker} {right}", flush=True)
        if marker == "->" and name in scaleup.get("reasons", {}):
            print(f"{'':28} reason   {scaleup['reasons'][name]}", flush=True)
    print("\nAssembly proof snapshot:", flush=True)
    print("  proof/assembly/compute_promise_minutes.s", flush=True)
    print("\nRuntime proof command:", flush=True)
    print("  make prove", flush=True)
    return 0


def assert_no_language_targets() -> None:
    offenders = []
    for path in sorted((ROOT / "specs").glob("*.angl")):
        if "Runs as:" in path.read_text():
            offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        raise RuntimeError(f"Angl specs still contain language targets: {offenders}")
    print("Angl source contains no language target hints.", flush=True)


def load_profile(name: str) -> dict:
    return json.loads((ROOT / "profiles" / f"{name}.json").read_text())


def selected_targets(data: dict) -> dict:
    selected = {unit: "python" for unit in UNITS}
    selected.update(data.get("targets", {}))
    return selected


def print_profile(name: str, targets: dict) -> None:
    print(f"\nprofiles/{name}.json", flush=True)
    for unit in UNITS:
        print(f"  {unit:28} {targets[unit]}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
