# /plumbline protect [owner/repo]

Apply protected-main as code. GitHub only (for Azure DevOps / GitLab, list the equivalent branch policies to set).

1. `gh auth status`; confirm admin: `gh api repos/<repo> --jq .permissions.admin`.
2. Prerequisites — list any missing:
   - `.github/rulesets/main-protection.json`, `scripts/protect-main.sh` (else `/plumbline init`)
   - `plumbline doctor` shows required checks match workflow job names
   - `ANTHROPIC_API_KEY` secret exists (`gh secret list`); without it `ai-architecture-review` is skipped and, being
     required, blocks every PR. Offer to drop it from the ruleset or wait.
   - both checks have run once on a PR
3. Show exactly what will change: ruleset (human code-owner approval that the last pusher can't give, stale
   approvals dismissed, no bypass actors, required checks, linear history); GitHub Actions can no longer approve
   PRs; squash-only merges; merged branches deleted. This affects everyone
   on the repo — get explicit confirmation.
4. Run `./scripts/protect-main.sh <repo>`.
5. Verify with `gh api repos/<repo>/rulesets --jq '.[].name'` and report. If rulesets are unavailable (private repo
   on GitHub Free), give the equivalent classic branch-protection settings.
