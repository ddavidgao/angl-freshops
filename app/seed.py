from __future__ import annotations

from app.db import pg


SCHEMA = """
drop table if exists promises;
drop table if exists orders;
drop table if exists courier_candidates;
drop table if exists substitution_candidates;
drop table if exists store_candidates;

create table orders (
  id text primary key,
  payload jsonb not null,
  status text not null default 'queued',
  created_at timestamptz not null default now()
);

create table promises (
  order_id text primary key references orders(id),
  payload jsonb not null,
  created_at timestamptz not null default now()
);

create table store_candidates (
  id text primary key,
  cost integer not null,
  value integer not null,
  risk_penalty integer not null,
  delay_penalty integer not null
);

create table substitution_candidates (
  id text primary key,
  cost integer not null,
  value integer not null,
  risk_penalty integer not null,
  delay_penalty integer not null
);

create table courier_candidates (
  id text primary key,
  cost integer not null,
  value integer not null,
  risk_penalty integer not null,
  delay_penalty integer not null
);
"""


def main() -> None:
    with pg() as conn:
        conn.execute(SCHEMA)
        with conn.cursor() as cur:
            cur.executemany(
                "insert into store_candidates values (%s, %s, %s, %s, %s)",
                [
                    ("north-market", 12, 88, 4, 2),
                    ("west-market", 12, 86, 1, 1),
                    ("hub-store", 12, 91, 2, 12),
                ],
            )
            cur.executemany(
                "insert into substitution_candidates values (%s, %s, %s, %s, %s)",
                [
                    ("oat-milk-for-milk", 2, 8, 1, 1),
                    ("brown-eggs-for-eggs", 1, 5, 0, 1),
                    ("bagels-for-bread", 2, 6, 1, 1),
                ],
            )
            cur.executemany(
                "insert into courier_candidates values (%s, %s, %s, %s, %s)",
                [
                    ("drop-17", 4, 9, 0, 1),
                    ("drop-22", 5, 10, 1, 2),
                    ("drop-40", 8, 11, 5, 6),
                ],
            )
    print("seeded FreshOps database")


if __name__ == "__main__":
    main()
