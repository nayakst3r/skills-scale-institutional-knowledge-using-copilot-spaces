.PHONY: check principles test

check: principles test

principles:
	python3 tools/check_principles.py .

test:
	python3 -m pytest tools/tests -q
