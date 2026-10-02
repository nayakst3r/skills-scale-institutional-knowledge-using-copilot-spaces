#!/usr/bin/env bash
# Selects the data stack for this repo: copies stacks/<stack>/overlay into place and records the choice.
# Everything else (principles, contracts, dbt models, checks, Copilot setup, PR process) is identical.
#
#   ./scripts/use-stack.sh                 # list stacks
#   ./scripts/use-stack.sh snowflake       # gcp | aws | azure-fabric | databricks | snowflake
#   ./scripts/use-stack.sh aws --force     # switch an already-configured repo (overwrites stack files)
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -eq 0 ]]; then
  echo "Stacks:"
  for s in stacks/*/stack.yaml; do
    printf "  %-14s %s\n" "$(basename "$(dirname "$s")")" "$(sed -n 's/^display_name: //p' "$s")"
  done
  exit 0
fi

STACK="$1"; FORCE="${2:-}"
SRC="stacks/$STACK"
[[ -f "$SRC/stack.yaml" ]] || { echo "unknown stack: $STACK (run without arguments to list)" >&2; exit 2; }
if [[ -f stack.yaml && "$FORCE" != "--force" ]]; then
  echo "stack already selected: $(sed -n 's/^stack: //p' stack.yaml). Use --force to switch." >&2; exit 1
fi

# Remove files a previous stack installed, so switching never leaves a mix behind.
if [[ -f .stack-files ]]; then
  while read -r f; do [[ -n "$f" ]] && rm -f "$f"; done < .stack-files
fi

cp "$SRC/stack.yaml" stack.yaml
( cd "$SRC/overlay" && find . -type f | sed 's#^\./##' ) > .stack-files
cp -R "$SRC/overlay/." .

# Put the stack's context into AGENTS.md so every engineer's Copilot knows it.
python3 - "$SRC/agents.md" <<'PY'
import re, sys
section = open(sys.argv[1]).read().strip()
text = open("AGENTS.md").read()
text = re.sub(r"<!-- stack:start -->.*?<!-- stack:end -->", f"<!-- stack:start -->\n{section}\n<!-- stack:end -->", text, flags=re.S)
open("AGENTS.md", "w").write(text)
PY

echo "Stack set to: $(sed -n 's/^display_name: //p' stack.yaml)"
echo
echo "Next:"
echo "  pip install -r requirements.txt -r requirements-stack.txt"
echo "  make check && make local-build"
echo "  Then read stacks/$STACK/README.md for the cloud setup (OIDC login, repo variables, environments)."
