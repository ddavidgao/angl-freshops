from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from psycopg.errors import UniqueViolation

from app.db import pg, redis_client


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"
QUEUE = "freshops-orders"

app = FastAPI(title="Angl FreshOps")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.post("/api/orders")
def create_order(payload: dict):
    order_id = payload.get("order_id") or f"O-{uuid.uuid4().hex[:8]}"
    payload = {**payload, "order_id": order_id}
    try:
        with pg() as conn:
            conn.execute(
                "insert into orders (id, payload, status) values (%s, %s, 'queued')",
                (order_id, json.dumps(payload)),
            )
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="order id already exists") from exc
    redis_client().lpush(QUEUE, order_id)
    return {"order_id": order_id, "status": "queued"}


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    with pg() as conn:
        order = conn.execute(
            "select status from orders where id = %s",
            (order_id,),
        ).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="order not found")
        promise = conn.execute(
            "select payload from promises where order_id = %s",
            (order_id,),
        ).fetchone()
    return {
        "order_id": order_id,
        "status": order[0],
        "promise": promise[0] if promise else None,
    }
