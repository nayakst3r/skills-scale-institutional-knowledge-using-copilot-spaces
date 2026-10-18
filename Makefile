# Kestrel meter data platform. Stack targets: ingest, build, test. Plumbline targets: check, check-all, setup.
GATE := python3 .plumbline/plumbline.py
BASE ?= origin/plumbline-demo

.PHONY: setup hooks ingest build test check check-all codeowners protect

setup:            ## install git hooks (Lefthook if configured, else .githooks)
	@if [ -f lefthook.yml ]; then (command -v lefthook >/dev/null && lefthook install) || npx --yes lefthook install; \
	else git config core.hooksPath .githooks; fi
	@echo "Hooks installed. Next: make check-all"

hooks:            ## regenerate lefthook.yml after adding a linter/formatter/type checker
	python3 .claude/skills/plumbline/run.py hooks --write --install

ingest:           ## parse the sample NEM12 files into landing/
	PYTHONPATH=src python3 -m kestrel.ingestion.nem12 sample_data/*.csv

build: ingest     ## dbt: seed, run and test every model on local DuckDB
	dbt build --profiles-dir .

test:             ## Python unit tests
	python3 -m pytest -q

check:            ## Plumbline gate on your branch's changes
	@git rev-parse --verify -q $(BASE) >/dev/null && $(GATE) --diff $(BASE) || $(GATE) --all

check-all:        ## Plumbline gate on the whole repository
	$(GATE) --all

codeowners:       ## regenerate .github/CODEOWNERS from ARCHITECTURE.md
	$(GATE) --codeowners .github/CODEOWNERS

protect:          ## apply main-branch protection (repo admin, gh CLI)
	./scripts/protect-main.sh
