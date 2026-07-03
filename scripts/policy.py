from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "profiles"


def apply_policy(units: dict) -> dict:
    targets = load_profile()["targets"]
    for name, target in targets.items():
        if name not in units:
            raise ValueError(f"policy target {name!r} does not match any Angl chapter")
        units[name]["target"] = target
    return units


def apply_policy_to_spec(spec: dict) -> dict:
    target = load_profile()["targets"].get(spec["name"])
    if target:
        spec["target"] = target
    return spec


def load_profile() -> dict:
    name = os.environ.get("ANGL_PROFILE") or os.environ.get("PROFILE") or "native"
    path = PROFILES / f"{name}.json"
    if not path.exists():
        raise ValueError(f"profile {name!r} does not exist at {path}")
    data = json.loads(path.read_text())
    targets = data.get("targets", {})
    if not isinstance(targets, dict):
        raise ValueError(f"profile {name!r} targets must be an object")
    data["name"] = data.get("name", name)
    data["targets"] = targets
    return data


def write_decision_manifest(build_dir: Path, units: dict) -> None:
    profile = load_profile()
    manifest = {
        "profile": profile["name"],
        "description": profile.get("description"),
        "constraints": profile.get("constraints", {}),
        "preferences": profile.get("preferences", {}),
        "chosen_targets": {
            name: spec.get("target", "python")
            for name, spec in sorted(units.items())
        },
    }
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / "profile.manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
