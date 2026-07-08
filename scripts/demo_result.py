from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build" / "latest"))

from build_delivery_promise import build_delivery_promise  # noqa: E402


def main() -> int:
    result = build_delivery_promise(
        {
            "order_id": "O-demo",
            "customer": " Mia ",
            "delivery_zone": "west",
            "priority": "express",
            "items": [
                {"id": " ice cream ", "qty": 1, "cold_chain": True},
                {"id": " milk ", "qty": 2},
            ],
        },
        [
            {"id": "north-market", "cost": 12, "value": 96, "risk_penalty": 4, "delay_penalty": 3},
            {"id": "west-market", "cost": 12, "value": 82, "risk_penalty": 1, "delay_penalty": 2},
        ],
        [
            {"id": "oat-milk-for-milk", "cost": 2, "value": 8, "risk_penalty": 1, "delay_penalty": 1},
            {"id": "brown-eggs-for-eggs", "cost": 1, "value": 5, "risk_penalty": 0, "delay_penalty": 1},
        ],
        [
            {"id": "drop-17", "cost": 4, "value": 9, "risk_penalty": 0, "delay_penalty": 1},
            {"id": "drop-22", "cost": 5, "value": 10, "risk_penalty": 1, "delay_penalty": 2},
        ],
        {"max_cost": 12, "risk": 3, "delay": 8, "substitution_budget": 3, "batch_minutes": 9},
    )
    visible = {
        "courier_batch": result["courier_batch"],
        "promised_minutes": result["promised_minutes"],
        "reasons": result["reasons"],
    }
    print(json.dumps(visible, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
