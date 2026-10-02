.PHONY: check principles test demo-step

check: principles test

principles:
	python3 tools/check_principles.py .

test:
	python3 -m pytest tools/tests -q

# Usage: make demo-step STEP=iteration-1-finance-domain   (no STEP = list the steps)
demo-step:
	./scripts/demo-step.sh $(STEP)
