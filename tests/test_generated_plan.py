from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build" / "latest"))

from build_delivery_promise import build_delivery_promise  # noqa: E402


def test_generated_delivery_promise():
    result = build_delivery_promise(
        {
            "order_id": "O-test",
            "customer": " Mia ",
            "delivery_zone": "west",
            "priority": "express",
            "items": [
                {"id": " ice cream ", "qty": 1, "cold_chain": True},
                {"id": " milk ", "qty": 2},
            ],
        },
        [
            {"id": "north-market", "cost": 12, "value": 88, "risk_penalty": 4, "delay_penalty": 2},
            {"id": "west-market", "cost": 12, "value": 86, "risk_penalty": 1, "delay_penalty": 1},
            {"id": "hub-store", "cost": 12, "value": 91, "risk_penalty": 2, "delay_penalty": 12},
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
    assert result == {
        "order_id": "O-test",
        "customer": "Mia",
        "store": "north-market",
        "substitutions": ["oat-milk-for-milk", "brown-eggs-for-eggs"],
        "courier_batch": [],
        "promised_minutes": 37,
        "reasons": ["delay penalties applied", "cold chain protected", "express priority"],
    }


if __name__ == "__main__":
    test_generated_delivery_promise()
    print("PASS test_generated_delivery_promise")
