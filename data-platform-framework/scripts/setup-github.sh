#!/usr/bin/env bash
# Applies the team's GitHub repository settings (Iteration 0 of the demo playbook).
#
#   ./scripts/setup-github.sh <owner>/<repo> [--solo] [--merge-queue]
#
#   --solo         Demo mode for a single presenter: 0 required approvals and no code-owner
#                  review (you can't approve your own PR). Everything else stays the same.
#   --merge-queue  Add a merge queue. Needs an organization-owned repo on a plan that supports it.
#
# Needs: gh CLI logged in as a repo admin (gh auth login).
set -euo pipefail

REPO="${1:?usage: setup-github.sh <owner>/<repo> [--solo] [--merge-queue]}"
shift
SOLO=false MERGE_QUEUE=false
for a in "$@"; do
  case "$a" in
    --solo) SOLO=true ;;
    --merge-queue) MERGE_QUEUE=true ;;
    *) echo "unknown flag: $a" >&2; exit 2 ;;
  esac
done

APPROVALS=1 CODE_OWNERS=true
if $SOLO; then APPROVALS=0 CODE_OWNERS=false; fi

echo "==> Merge settings: squash only, PR title becomes the commit, delete branch on merge"
gh api -X PATCH "repos/$REPO" --silent \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true -F allow_auto_merge=true \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY

echo "==> Ruleset 'main-protection' on the default branch"
MQ_RULE=""
if $MERGE_QUEUE; then
  MQ_RULE=',{"type":"merge_queue","parameters":{
      "merge_method":"SQUASH","grouping_strategy":"ALLGREEN",
      "max_entries_to_build":5,"max_entries_to_merge":5,"min_entries_to_merge":1,
      "min_entries_to_merge_wait_minutes":1,"check_response_timeout_minutes":30}}'
fi

# Safe to re-run: update the ruleset in place if it already exists.
RULESET_ID=$(gh api "repos/$REPO/rulesets" --jq '.[] | select(.name=="main-protection") | .id')
if [[ -n "$RULESET_ID" ]]; then METHOD=PUT URL="repos/$REPO/rulesets/$RULESET_ID"; else METHOD=POST URL="repos/$REPO/rulesets"; fi

gh api -X "$METHOD" "$URL" --silent --input - <<JSON
{
  "name": "main-protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": $APPROVALS,
        "require_code_owner_review": $CODE_OWNERS,
        "dismiss_stale_reviews_on_push": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true } },
    { "type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [
          { "context": "principles" },
          { "context": "local-build" },
          { "context": "lint" },
          { "context": "secrets" },
          { "context": "stack-validate" }
        ] } }
    $MQ_RULE
  ]
}
JSON

echo "==> Labels"
for l in "feature:0e8a16" "breaking-change:b60205" "needs-architecture:5319e7" "platform:1d76db"; do
  gh label create "${l%%:*}" --color "${l##*:}" --repo "$REPO" --force >/dev/null
done

echo "==> Environments (add required reviewers to 'prod' in Settings → Environments)"
for e in ci stg prod; do gh api -X PUT "repos/$REPO/environments/$e" --silent; done

cat <<EOF

Done. Remaining manual steps (they need org-admin rights or cloud access):
  1. Create the GitHub teams named in .github/CODEOWNERS (or replace @org/... with your teams).
  2. Settings → Environments → prod: add the release captain as a required reviewer.
  3. Settings → Code security: turn on secret scanning + push protection, if available to you.
  4. Settings → Copilot → Coding agent: enable it for this repo, and turn on automatic Copilot code review.
  5. Connect your cloud: follow stacks/<stack>/README.md and set the variables it lists
     ($(sed -n 's/^ci_variables: //p' stack.yaml 2>/dev/null || echo "run scripts/use-stack.sh first")).
     Until they exist, the cloud steps are skipped and the offline checks still run.
EOF
