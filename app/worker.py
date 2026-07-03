from __future__ import annotations

import json
import time

from psycopg.rows import dict_row

from app.db import pg, redis_client
from app.generated import build_delivery_promise


QUEUE = "freshops-orders"
TABLES = {
    "stores": "store_candidates",
    "substitutions": "substitution_candidates",
    "couriers": "courier_candidates",
}


def main() -> None:
    r = redis_client()
    print("freshops worker listening")
    while True:
        item = r.brpop(QUEUE, timeout=2)
        if not item:
            continue
        _, order_id = item
        handle_order(order_id)


def handle_order(order_id: str) -> None:
    try:
        process_order(order_id)
    except Exception as exc:
        with pg() as conn:
            conn.execute(
                "update orders set status = %s where id = %s",
                (f"failed: {exc}", order_id),
            )
        print(f"failed {order_id}: {exc}")


def process_order(order_id: str) -> None:
    with pg() as conn:
        order = conn.execute(
            "select payload from orders where id = %s",
            (order_id,),
        ).fetchone()
        if not order:
            return
        payload = order[0]
        pressure = payload.get("pressure")
        if not isinstance(pressure, dict):
            raise ValueError("order payload must include pressure")
        store_candidates = _rows(conn, "stores")
        substitution_candidates = _rows(conn, "substitutions")
        courier_candidates = _rows(conn, "couriers")
        promise = build_delivery_promise(
            payload,
            store_candidates,
            substitution_candidates,
            courier_candidates,
            pressure,
        )
        conn.execute(
            """
            insert into promises (order_id, payload)
            values (%s, %s)
            on conflict (order_id) do update set payload = excluded.payload
            """,
            (order_id, json.dumps(promise)),
        )
        conn.execute("update orders set status = 'promised' where id = %s", (order_id,))
    print(f"promised {order_id}")


def _rows(conn, kind: str) -> list[dict]:
    table = TABLES[kind]
    with conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(
            f"select id, cost, value, risk_penalty, delay_penalty from {table} order by id"
        ).fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    main()
