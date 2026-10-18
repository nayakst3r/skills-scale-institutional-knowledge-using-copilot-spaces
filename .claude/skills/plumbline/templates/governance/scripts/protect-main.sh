#!/usr/bin/env bash
# Apply branch protection as code. Needs: gh CLI authenticated as a repo admin.
# Rulesets on private repos need GitHub Team, Enterprise Cloud or Enterprise Server.
set -euo pipefail
REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
RULESET="$(dirname "$0")/../.github/rulesets/main-protection.json"
NAME=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' "$RULESET")

echo "Repository settings: squash-only merges, delete merged branches"
gh api -X PATCH "repos/$REPO" -F allow_squash_merge=true -F allow_merge_commit=false \
  -F allow_rebase_merge=false -F delete_branch_on_merge=true -F allow_auto_merge=false >/dev/null

ID=$(gh api "repos/$REPO/rulesets" --jq ".[] | select(.name==\"$NAME\") | .id" || true)
if [ -n "$ID" ]; then
  echo "Updating ruleset '$NAME' ($ID)"
  gh api -X PUT "repos/$REPO/rulesets/$ID" --input "$RULESET" >/dev/null
else
  echo "Creating ruleset '$NAME'"
  gh api -X POST "repos/$REPO/rulesets" --input "$RULESET" >/dev/null
fi

echo "Human review: GitHub Actions may not approve pull requests"
gh api -X PUT "repos/$REPO/actions/permissions/workflow" -F can_approve_pull_request_reviews=false >/dev/null

echo "Triage labels (see docs/agents/triage-labels.md)"
for spec in "needs-triage:ededed" "needs-human-approval:fbca04" "ready-for-agent:0e8a16" "ready-for-human:1d76db" \
            "wontfix:ffffff" "spec:5319e7"; do
  gh label create "${spec%%:*}" --color "${spec##*:}" --force -R "$REPO" >/dev/null
done

echo "Enabling private vulnerability reporting"
gh api -X PUT "repos/$REPO/private-vulnerability-reporting" >/dev/null 2>&1 || echo "  (skipped - not available for this repo)"
echo "Done. main now requires: a human code-owner approval (not the last pusher, no bypass), plumbline-gate,"
echo "ai-architecture-review, resolved threads and linear history. Actions cannot approve PRs."
