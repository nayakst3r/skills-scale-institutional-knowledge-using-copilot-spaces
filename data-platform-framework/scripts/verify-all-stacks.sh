#!/usr/bin/env bash
# Framework maintainers: proves the template works on every stack. For each stack, in a temp copy:
# apply the stack, run the architecture checks, `dbt parse` offline with the stack's own adapter,
# and a full local build on DuckDB. Needs every adapter installed (see stacks/*/overlay/requirements-stack.txt).
set -uo pipefail
cd "$(dirname "$0")/.."
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
STATUS=0
for s in ${*:-gcp aws azure-fabric databricks snowflake}; do
  echo "== $s"
  W="$WORK/$s"; mkdir -p "$W"
  tar --exclude=./target --exclude=./.git -cf - . | tar -xf - -C "$W"
  (
    cd "$W" || exit 1
    ./scripts/use-stack.sh "$s" >/dev/null &&
    python3 tools/check_principles.py . | tail -1 &&
    DBT_TARGET=ci timeout 120 dbt parse --no-partial-parse -q > parse.log 2>&1 && echo "dbt parse (ci, $(sed -n 's/^adapter: //p' stack.yaml)): OK" &&
    make -s local-build > build.log 2>&1 && echo "local build: OK ($(grep -o 'PASS=[0-9]*' build.log | tail -1))"
  ) || { echo "FAILED: $s"; tail -5 "$W/parse.log" "$W/build.log" 2>/dev/null; STATUS=1; }
done
exit $STATUS
