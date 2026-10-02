.PHONY: check principles test local-build use-stack demo-step

check: principles test

principles:
	python3 tools/check_principles.py .

test:
	python3 -m pytest tools/tests -q

# Build + test every model on DuckDB with sample_data/ (no cloud account needed)
local-build:
	DBT_TARGET=local dbt seed --full-refresh --quiet && DBT_TARGET=local dbt build --exclude resource_type:seed

# Usage: make use-stack STACK=snowflake   (gcp | aws | azure-fabric | databricks | snowflake)
use-stack:
	./scripts/use-stack.sh $(STACK)

# Usage: make demo-step STEP=iteration-1-finance-domain   (no STEP = list the steps)
demo-step:
	./scripts/demo-step.sh $(STEP)
