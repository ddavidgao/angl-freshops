ANGL_REPO ?= ../angl
PROFILE ?= native
ANGL_MODEL_PROVIDER ?= claude-code
ANGL_MODEL ?= sonnet
ANGL_MODEL_TIMEOUT ?= 180

.PHONY: build verify seed run-api run-worker test proof demo-profiles demo prove clean

build:
	ANGL_REPO=$(ANGL_REPO) ANGL_PROFILE=$(PROFILE) ANGL_MODEL_PROVIDER=$(ANGL_MODEL_PROVIDER) ANGL_MODEL=$(ANGL_MODEL) ANGL_MODEL_TIMEOUT=$(ANGL_MODEL_TIMEOUT) .venv/bin/python scripts/compile_angl.py

verify:
	ANGL_REPO=$(ANGL_REPO) ANGL_PROFILE=$(PROFILE) .venv/bin/python scripts/verify_angl.py

seed:
	.venv/bin/python -m app.seed

run-api:
	.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8810

run-worker:
	.venv/bin/python -m app.worker

test: verify
	.venv/bin/python tests/test_assembly_runtime.py
	.venv/bin/python tests/test_generated_plan.py
	.venv/bin/python tests/test_full_stack_flow.py

proof:
	ANGL_REPO=$(ANGL_REPO) ANGL_PROFILE=$(PROFILE) .venv/bin/python scripts/proof.py

demo-profiles:
	ANGL_REPO=$(ANGL_REPO) .venv/bin/python scripts/demo_profiles.py

demo: demo-profiles

prove:
	$(MAKE) proof PROFILE=scaleup

clean:
	rm -rf build __pycache__ app/__pycache__ tests/__pycache__
