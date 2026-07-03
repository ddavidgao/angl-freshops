# Angl FreshOps

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
  build_delivery_promise.angl
```

Selection chapters use Angl's bundle target. A bundle can contain multiple
generated files and build steps. In the current verified run, the model chose
Python bundle files; native or assembly bundle output should be treated as a
separate proof, not claimed unless the generated edition actually contains it.

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
2. Deletes generated output.
3. Rebuilds `build/latest/` from `.angl` chapters.
4. Verifies every chapter with the Angl judge.
5. Runs app-level integration tests.
6. Starts the worker and API.
7. Submits a real HTTP order and checks the saved promise.

## Why This Is Not One-Shot Claude

One-shot Claude gives you generated source code, then every behavior change
becomes another conversation.

FreshOps keeps the durable edit in Angl. If the substitution policy changes,
edit the substitution chapter and its examples, rebuild, and let the judge
accept or reject the generated edition.
