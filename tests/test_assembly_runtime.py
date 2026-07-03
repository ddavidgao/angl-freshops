from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "latest"
sys.path.insert(0, str(BUILD))

from compute_promise_minutes import compute_promise_minutes  # noqa: E402


def test_assembly_runtime_is_present_and_used():
    manifest = json.loads((BUILD / "compute_promise_minutes.manifest.json").read_text())
    host_adapter = (BUILD / manifest["host_adapter"]).read_text()
    assembly = (BUILD / manifest["implementation"]).read_text()
    top_level = (BUILD / "build_delivery_promise.py").read_text()

    assert manifest["target"] == "assembly"
    assert manifest["implementation"].endswith(".s")
    assert any("clang" in command for command in manifest["build"][0])
    assert (BUILD / "libcompute_promise_minutes.dylib").exists()
    assert "ctypes.CDLL" in host_adapter
    assert re.search(r"\.glob(?:a)?l\s+_compute_promise_minutes", assembly)
    assert re.search(r"_compute_promise_minutes\w*:", assembly)
    assert "from compute_promise_minutes import compute_promise_minutes" in top_level
    assert "compute_promise_minutes(35" in top_level
    assert compute_promise_minutes(35, 12, 9) == 56


if __name__ == "__main__":
    test_assembly_runtime_is_present_and_used()
    print("PASS test_assembly_runtime")
