SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help install dev deploy test test-e2e test-e2e-running check clean

help:
	@echo "Available commands:"
	@echo "  make install            Install dependencies with uv"
	@echo "  make dev                Start local worker dev server"
	@echo "  make deploy             Deploy worker"
	@echo "  make test               Run all tests"
	@echo "  make test-e2e           Run end-to-end API tests"
	@echo "  make test-e2e-running   Run e2e tests against an already running server"
	@echo "  make check              Run syntax checks and tests"
	@echo "  make clean              Remove Python caches and pytest cache"

install:
	uv sync

dev:
	uv run pywrangler dev

deploy:
	uv run pywrangler deploy

test:
	uv run pytest

test-e2e:
	uv run pytest tests/e2e -m e2e

test-e2e-running:
	E2E_START_SERVER=0 uv run pytest tests/e2e -m e2e

check:
	uv run python -m compileall src
	uv run pytest -q

clean:
	find src -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf .pytest_cache
