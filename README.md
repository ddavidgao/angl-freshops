# Angl FreshOps

Source of truth: `.angl` chapters in `specs/`. Runtime: generated code plus
minimal local app plumbing.

FreshOps is a local grocery delivery promise engine built around Angl.

The app is easy to understand:

1. A customer submits a grocery order.
2. The system chooses the fulfillment store.
3. It chooses acceptable substitutions.
4. It chooses courier work to batch.
5. It returns a delivery promise.

The backend is intentionally real enough to matter:

- Postgres stores inventory, couriers, orders, and promises.
- Redis queues order-planning jobs.
- A worker consumes jobs and calls generated Angl code.
- The browser talks to an API and polls job status.

The point is not that the UI is generated. The point is that the product
decisions live in `.angl` chapters, not in a chat transcript and not in
hand-written business logic.

## Source Of Truth

```text
specs/
  normalize_order.angl
  choose_fulfillment_store.angl
  choose_substitution_pack.angl
  choose_courier_batch.angl
  compute_promise_minutes.angl
  build_delivery_promise.angl
```

`compute_promise_minutes.angl` runs as Angl's `assembly` target. The generated
edition contains ARM64 assembly, compiles it with local `clang` into
`libcompute_promise_minutes.dylib`, and calls it from the generated host adapter
with `ctypes`.

A checked-in proof snapshot of that generated assembly lives at:

```text
proof/assembly/compute_promise_minutes.s
```

The snapshot is not the source of truth; it exists so GitHub and reviewers can
see the assembly output without running the compiler first.

Selection chapters use Angl's `bundle` and `python` targets. A bundle can
contain multiple generated files and build steps. The generated edition is still
disposable; the durable behavior remains in `specs/`.

The generated edition lands in:

```text
build/latest/
```

`build/latest/` is disposable generated output. The durable source is the Angl
chapter catalog under `specs/`.

## Run

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
docker compose up -d postgres redis
make seed
ANGL_MODEL_PROVIDER=claude-code ANGL_MODEL=sonnet make build
make run-worker
make run-api
```

Then open:

```text
http://127.0.0.1:8810
```

## Proof Command

After installing the venv, run the full local proof:

```bash
ANGL_MODEL_PROVIDER=claude-code ANGL_MODEL=sonnet make proof
```

This command:

1. Starts Postgres and Redis.
2. Builds missing or stale generated output from `.angl` chapters.
3. Verifies every chapter with the Angl judge.
4. Checks that `compute_promise_minutes` really generated `.s`, built a
   `.dylib`, and is imported by the composed generated code.
5. Runs app-level integration tests.
6. Starts the worker and API.
7. Submits a real HTTP order and checks the saved promise.

For a cold regeneration proof, run:

```bash
make clean
ANGL_MODEL_PROVIDER=claude-code ANGL_MODEL=sonnet make proof
```

## Why This Is Not One-Shot Claude

One-shot Claude gives you generated source code, then every behavior change
becomes another conversation.

FreshOps keeps the durable edit in Angl. If the substitution policy changes,
edit the substitution chapter and its examples, rebuild, and let the judge
accept or reject the generated edition.

## What This Proves

This repo is not claiming the whole app is handwritten assembly. It proves a
narrower and more useful thing: the product decisions are durable `.angl`
chapters, while the runnable edition is generated and verified. One chapter is
generated as real ARM64 assembly and used by the composed app.

GitHub does not know Angl as a language yet, so `.gitattributes` avoids mapping
`.angl` to a fake language and marks host/proof plumbing as vendored. Read
`specs/` first. That is the source of truth. `app/`, `scripts/`, and `tests/`
are the minimum runtime and proof plumbing needed to make the Angl chapters run
as a real local app.
