from __future__ import annotations

import sys
from pathlib import Path

from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db import pg, redis_client
from app.seed import main as seed
from app.server import create_order, get_order
from app.worker import QUEUE, handle_order, process_order


def reset_state():
    seed()
    redis_client().delete(QUEUE)


def test_full_stack_order_flow():
    reset_state()

    created = create_order(
        {
            "customer": "Mia",
            "delivery_zone": "west",
            "items": [
                {"id": " milk ", "qty": 2},
                {"id": "eggs", "qty": 1},
            ],
            "pressure": {
                "max_cost": 12,
                "risk": 3,
                "delay": 8,
                "substitution_budget": 3,
                "batch_minutes": 9,
            },
        }
    )
    assert created["status"] == "queued"

    process_order(created["order_id"])
    result = get_order(created["order_id"])

    assert result["status"] == "promised"
    assert result["promise"]["customer"] == "Mia"
    assert result["promise"]["store"] == "north-market"
    assert "delay penalties applied" in result["promise"]["reasons"]
    assert result["promise"]["courier_batch"] == ["drop-17", "drop-22"]


def test_duplicate_order_id_returns_conflict():
    reset_state()
    order = {
        "order_id": "O-fixed",
        "customer": "Mia",
        "items": [{"id": "milk", "qty": 1}],
        "pressure": {
            "max_cost": 12,
            "risk": 3,
            "delay": 2,
            "substitution_budget": 3,
            "batch_minutes": 9,
        },
    }
    create_order(order)
    try:
        create_order(order)
    except HTTPException as exc:
        assert exc.status_code == 409
    else:
        raise AssertionError("duplicate order id should return 409")


def test_missing_pressure_marks_order_failed():
    reset_state()
    order_id = "O-no-pressure"
    with pg() as conn:
        conn.execute(
            "insert into orders (id, payload, status) values (%s, %s, 'queued')",
            (order_id, '{"order_id":"O-no-pressure","customer":"Mia","items":[{"id":"milk","qty":1}]}'),
        )

    handle_order(order_id)

    with pg() as conn:
        status = conn.execute(
            "select status from orders where id = %s",
            (order_id,),
        ).fetchone()[0]
    assert "failed:" in status
    assert "pressure" in status


if __name__ == "__main__":
    test_full_stack_order_flow()
    test_duplicate_order_id_returns_conflict()
    test_missing_pressure_marks_order_failed()
    print("PASS test_full_stack_flow")
