ANGL_REPO ?= ../angl

.PHONY: build verify seed run-api run-worker test proof clean

build:
	ANGL_REPO=$(ANGL_REPO) .venv/bin/python scripts/compile_angl.py

verify:
	ANGL_REPO=$(ANGL_REPO) .venv/bin/python scripts/verify_angl.py

seed:
	.venv/bin/python -m app.seed

run-api:
	.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8810

run-worker:
	.venv/bin/python -m app.worker

test: verify
	.venv/bin/python tests/test_generated_plan.py
	.venv/bin/python tests/test_full_stack_flow.py

proof:
	ANGL_REPO=$(ANGL_REPO) .venv/bin/python scripts/proof.py

clean:
	rm -rf build __pycache__ app/__pycache__ tests/__pycache__
