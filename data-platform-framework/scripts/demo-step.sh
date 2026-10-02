#!/usr/bin/env bash
# Applies a demo step's reference solution on top of the working tree.
# This is the presenter's fallback if live Copilot output goes off track. See docs/DEMO_PLAYBOOK.md.
# A step has common/ files (dbt models and contracts: the same on every stack) and, when needed,
# stacks/<stack>/ files (orchestration) for the stack selected with use-stack.sh.
#
#   ./scripts/demo-step.sh                      # list steps
#   ./scripts/demo-step.sh iteration-1-finance-domain
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -eq 0 ]]; then
  echo "Demo steps:"; ls demo | sed 's/\.patch$//' | sed 's/^/  /'; exit 0
fi

STEP="${1%.patch}"
STACK="$(sed -n 's/^stack: //p' stack.yaml 2>/dev/null || true)"
if [[ -f "demo/$STEP.patch" ]]; then
  git apply "demo/$STEP.patch"
elif [[ -d "demo/$STEP/common" ]]; then
  cp -R "demo/$STEP/common/." .
  if [[ -d "demo/$STEP/stacks" ]]; then
    if [[ -n "$STACK" && -d "demo/$STEP/stacks/$STACK" ]]; then
      cp -R "demo/$STEP/stacks/$STACK/." .
    else
      echo "note: no stack selected, so this step's orchestration files were skipped (run scripts/use-stack.sh)"
    fi
  fi
else
  echo "no such step: $STEP" >&2; exit 2
fi
echo "Applied $STEP${STACK:+ for $STACK}. Changed files:"
git status --short
