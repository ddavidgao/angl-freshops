# Angl FreshOps

FreshOps is a small grocery-delivery promise engine built to test Angl on a
real local app shape.

The durable behavior is written as `.angl` chapters in `specs/`, with shared
data shapes in `schemas/`. The runnable edition is generated, verified, and
then used by a normal backend with Postgres, Redis, a worker, and an HTTP API.

## What It Does

A customer submits a grocery order. FreshOps:

1. Normalizes the order.
2. Chooses a fulfillment store.
3. Chooses acceptable substitutions.
4. Chooses courier stops to batch, unless cold-chain items require direct delivery.
5. Computes the promised delivery time.
6. Saves the promise back to Postgres.

The interesting part is where the product decisions live. Store choice,
substitution policy, courier batching, and promise timing are not edited in the
host app. They are edited in Angl chapters and regenerated into disposable code.

## Angl Source

```text
specs/
  normalize_order.angl
  choose_fulfillment_store.angl
  choose_substitution_pack.angl
  choose_courier_batch.angl
  compute_promise_minutes.angl
  build_delivery_promise.angl

schemas/
  Order.schema.json
  Candidate.schema.json
  Pressure.schema.json
  DeliveryPromise.schema.json
```

Each chapter has:

- A typed boundary.
- Natural-language behavior.
- Executable examples that the judge enforces.

Schemas make the data contracts explicit without putting implementation stack
choices into the Angl source.

`build/latest/` is generated output. It is intentionally ignored by git.

## Runtime Shape

```text
browser
  -> FastAPI
  -> Postgres orders table
  -> Redis queue
  -> worker
  -> generated Angl edition in build/latest/
  -> Postgres promises table
```

Handwritten Python is glue: API, database access, queue worker, proof scripts,
and tests. Product behavior is in `specs/`.

## Proof

After installing dependencies, run:

```bash
angl build specs --build-dir build/latest
angl verify specs --build-dir build/latest
python3 scripts/proof.py
```

This command:

1. Starts Postgres and Redis.
2. Builds generated output from `.angl` using the public Angl CLI.
3. Verifies every chapter with Angl's black-box judge.
4. Runs app-level integration tests.
5. Starts the worker and API.
6. Submits a real HTTP order and checks the saved promise.

For a cold regeneration run:

```bash
rm -rf build/latest
angl build specs --build-dir build/latest
angl verify specs --build-dir build/latest
python3 scripts/proof.py
```

Cold regeneration can take several minutes because it asks the model to rebuild
every chapter.

## Run Locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
docker compose up -d postgres redis
angl build specs --build-dir build/latest
python3 -m app.seed
.venv/bin/python -m app.worker
.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8810
```

Open:

```text
http://127.0.0.1:8810
```

FreshOps uses the configured Angl compiler provider. Set it once with
`angl setup codex`, `angl setup claude-code`, or `angl setup ollama`. Every
subsequent `angl build` uses that saved provider configuration.

## What This Repo Is Proving

The goal was not to build a large grocery product. The goal was to check whether
Angl can own meaningful backend behavior while the generated code stays
replaceable.

FreshOps now demonstrates:

- A real app boundary around Angl-generated code.
- Multiple Angl chapters composed together.
- Shared schemas for the real data shapes.
- Black-box verification for every chapter.
- Postgres and Redis in the runtime path.
- A repeatable proof command that exercises the whole path.

GitHub does not know Angl as a language yet. `.gitattributes` keeps host and
proof plumbing from dominating the language bar. The source of truth remains
`specs/`.
