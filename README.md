# Angl FreshOps

FreshOps is a small grocery-delivery promise engine built to test Angl on a
real local app shape.

The durable behavior is written as `.angl` chapters in `specs/`. The runnable
edition is generated, verified, and then used by a normal backend with Postgres,
Redis, a worker, and an HTTP API.

## What It Does

A customer submits a grocery order. FreshOps:

1. Normalizes the order.
2. Chooses a fulfillment store.
3. Chooses acceptable substitutions.
4. Chooses courier stops to batch.
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
```

Each chapter has:

- A typed boundary.
- Natural-language behavior.
- Executable examples that the judge enforces.

`build/latest/` is generated output. It is intentionally ignored by git.

## Assembly Proof

`compute_promise_minutes.angl` runs as Angl's `assembly` target. During build,
Angl generates ARM64 assembly, compiles it with local `clang` into a dylib, and
generates a Python host adapter that calls the dylib through `ctypes`.

The live app uses that generated function when computing `promised_minutes`.

A checked-in proof snapshot is here:

```text
proof/assembly/compute_promise_minutes.s
```

That snapshot is not the source of truth. It exists so reviewers can see the
assembly output without running the compiler first.

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
ANGL_MODEL_PROVIDER=claude-code ANGL_MODEL=sonnet make proof
```

This command:

1. Starts Postgres and Redis.
2. Builds missing or stale generated output from `.angl`.
3. Verifies every chapter with Angl's black-box judge.
4. Checks that the assembly chapter generated `.s`, built a dylib, and is used
   by the composed generated code.
5. Runs app-level integration tests.
6. Starts the worker and API.
7. Submits a real HTTP order and checks the saved promise.

For a cold regeneration run:

```bash
make clean
ANGL_MODEL_PROVIDER=claude-code ANGL_MODEL=sonnet make proof
```

Cold regeneration can take several minutes because it asks the model to rebuild
every chapter.

## Run Locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
docker compose up -d postgres redis
make seed
ANGL_MODEL_PROVIDER=claude-code ANGL_MODEL=sonnet make build
make run-worker
make run-api
```

Open:

```text
http://127.0.0.1:8810
```

## What This Repo Is Proving

The goal was not to build a large grocery product. The goal was to check whether
Angl can own meaningful backend behavior while the generated code stays
replaceable.

FreshOps now demonstrates:

- A real app boundary around Angl-generated code.
- Multiple Angl chapters composed together.
- Black-box verification for every chapter.
- Postgres and Redis in the runtime path.
- One generated ARM64 assembly chapter used by the live app.
- A repeatable proof command that exercises the whole path.

GitHub does not know Angl as a language yet. `.gitattributes` keeps host and
proof plumbing from dominating the language bar and includes an assembly proof
snapshot for visibility. The source of truth remains `specs/`.
