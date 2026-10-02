# Contributing: check-ins, PRs, and merges

## 1. Branching — trunk-based

- `main` is always deployable to stg. It's protected: no direct pushes, no force pushes.
- Short-lived branches off `main`, **≤ 2 days**, named `<type>/<domain>-<issue>-<slug>`:
  - `feat/sales-123-daily-revenue`, `fix/finance-88-null-currency`, `chore/platform-41-bump-dbt`
- No `develop` or long-running feature branches. Hide unfinished work behind a flag
  (a dbt `enabled` config driven by a var, or an unscheduled job) instead of a long branch.
- Rebase on or merge `main` daily; the merge queue does the final rebase.

## 2. Check-ins (commits)

- **Conventional Commits**: `type(scope): summary`, for example `feat(sales): add revenue_daily gold table`.
  Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`. Scope = domain or `platform`/`libs`.
  `!` marks a breaking change: `feat(sales)!: v2 orders contract`.
- Pre-commit hooks must pass (`pre-commit install` once). Never `--no-verify`.
- AI-assisted commits are fine; add `Assisted-by: <tool>` in the trailer. **You** are the author and are accountable.

## 3. Pull requests

- **Small**: one concern, aim for < 400 changed lines. Split AI-generated bulk changes.
- **Separate PRs** for platform/`libs/` changes and for domain features that use them.
- Fill in the PR template completely, especially *Contracts touched* and *Breaking change?*.
- Open as **Draft** early; mark **Ready** when CI is green.
- Link the issue (`Closes #123`).

### Required checks (branch protection on `main`)
| Check | What it does |
|---|---|
| `principles` | `tools/check_principles.py`: architecture checks, plus contract compatibility vs `main` (fails on a breaking change) |
| `local-build` | `dbt build` of every model and test on DuckDB with `sample_data/` |
| `stack-validate` | Offline `dbt parse` with the stack's adapter and `terraform validate`; once connected, `dbt build --empty` in the real warehouse |
| `lint` | ruff, terraform fmt |
| `secrets` | gitleaks |

### Reviews
- **1 approval from CODEOWNERS** of each touched path; **2** if `platform/`, `libs/`, or any `contracts/` file changes.
- AI review (Copilot / Gemini Code Assist) runs automatically and is **advisory**: it never counts as an approval.
- Reviewers check the [review checklist](#review-checklist), not style (linters own style).
- Turnaround target: first review within **4 working hours**.
- "Dismiss stale approvals on new commits" is on.

## 4. Merging

- **Merge queue** enabled on `main`; method: **squash merge** (PR title becomes the commit, so it must be a Conventional Commit).
- Author merges (via queue) once approved and green; reviewers don't merge for you.
- Delete the branch after merge (automatic).

## 5. Release and deploy

| Env | Trigger | Gate |
|---|---|---|
| local | engineer runs `make local-build` (DuckDB) | none |
| dev sandbox | engineer runs `DBT_TARGET=dev DBT_USER=<you> dbt build --select tag:<domain>` (schemas `sbx_<you>_*`) | none |
| stg | every merge to `main` | CI green; `dbt build` (with data tests) in stg |
| prod | git tag `vYYYY.MM.DD.N` | GitHub Environment `prod`: 1 approval from release captain + stg green for 24h |

Rollback = re-deploy the previous tag. Data rollback = the warehouse's time travel (Delta, Iceberg, Snowflake, BigQuery, and Fabric all have it) or re-run from bronze.

## Review checklist
- [ ] Follows the principles in `ARCHITECTURE.md` (the parts CI can't check: idempotency, partitioning choice, naming clarity)
- [ ] Contract updated and compatible; consumers notified if deprecating
- [ ] Tests or assertions cover the new logic
- [ ] No unexplained AI-generated code: the author can explain every line
- [ ] Backfill and re-run behaviour considered
- [ ] Cost: partition filter present on large tables
