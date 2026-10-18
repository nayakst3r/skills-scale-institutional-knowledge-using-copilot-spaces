# Stack-specific targets (test) are filled in by /plumbline new or by your team.
GATE := python3 .plumbline/plumbline.py
BASE ?= origin/__DEFAULT_BRANCH__

.PHONY: setup hooks test check check-all codeowners protect

setup:            ## install git hooks (Lefthook if configured, else .githooks)
	@if [ -f lefthook.yml ]; then (command -v lefthook >/dev/null && lefthook install) || npx --yes lefthook install; \
	else git config core.hooksPath .githooks; fi
	@echo "Hooks installed. Next: make check-all"

hooks:            ## regenerate lefthook.yml after adding a linter/formatter/type checker
	python3 .claude/skills/plumbline/run.py hooks --write --install

test:             ## run the test suite (replace with your stack's runner)
	@if [ -f pyproject.toml ]; then python3 -m pytest -q; \
	elif [ -f package.json ]; then npm test --silent; \
	elif ls *.sln >/dev/null 2>&1; then dotnet test; \
	else echo "No test runner configured yet"; fi

check:            ## Plumbline gate on your branch's changes
	@git rev-parse --verify -q $(BASE) >/dev/null && $(GATE) --diff $(BASE) || $(GATE) --all

check-all:        ## Plumbline gate on the whole repository
	$(GATE) --all

codeowners:       ## regenerate .github/CODEOWNERS from ARCHITECTURE.md
	$(GATE) --codeowners .github/CODEOWNERS

protect:          ## apply main-branch protection (repo admin, gh CLI)
	./scripts/protect-main.sh
