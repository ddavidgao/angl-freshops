from __future__ import annotations

import os

import psycopg
import redis


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://freshops:freshops@127.0.0.1:5544/freshops",
)
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6385/0")


def pg():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def redis_client():
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)
