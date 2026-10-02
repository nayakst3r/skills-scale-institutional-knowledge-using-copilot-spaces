#!/usr/bin/env bash
# Applies a demo step's reference solution on top of the working tree.
# This is the presenter's fallback if live Copilot output goes off track. See docs/DEMO_PLAYBOOK.md.
#
#   ./scripts/demo-step.sh                      # list steps
#   ./scripts/demo-step.sh iteration-1-finance-domain
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -eq 0 ]]; then
  echo "Demo steps:"; ls demo | sed 's/\.patch$//' | sed 's/^/  /'; exit 0
fi

STEP="${1%.patch}"
if [[ -f "demo/$STEP.patch" ]]; then
  git apply "demo/$STEP.patch"
elif [[ -d "demo/$STEP" ]]; then
  cp -R "demo/$STEP/." .
else
  echo "no such step: $STEP" >&2; exit 2
fi
echo "Applied $STEP. Changed files:"
git status --short
