# AGENTS.md — Shared context for every AI assistant and every engineer

You are working in the team's data platform monorepo. Read this file and `ARCHITECTURE.md`
before writing code. If a request conflicts with these rules, stop and say so instead of
working around them.

## How the platform is built (all stacks)
- Transformations: **dbt**, one project (`dbt_project.yml`), models in `domains/<domain>/models/`.
- Contracts: `domains/<domain>/contracts/<table>.yaml`, with **logical** types (`string`, `integer`, `decimal`, `date`, `timestamp`, …).
- Orchestration: `domains/<domain>/orchestration/` only *schedules* dbt (`dbt build --select tag:<domain>`).
- Infra: **Terraform** in `platform/terraform/`. CI/CD: GitHub Actions with OIDC (no stored cloud keys).
- Python 3.11, `ruff`; run everything locally with `make local-build` (DuckDB, no cloud needed).

<!-- stack:start -->
## This repo's stack
No stack selected yet. Run `./scripts/use-stack.sh <gcp|aws|azure-fabric|databricks|snowflake>`.
<!-- stack:end -->

## Hard rules (CI enforces these — see `tools/check_principles.py`)
1. **Model files are named `<domain>_<layer>_<table>.sql`** (layer = bronze, silver, or gold) in `domains/<domain>/models/`. Don't set `schema` or `alias` in models; `macros/naming.sql` derives them.
2. **Every model needs a contract** at `domains/<domain>/contracts/<table>.yaml` with the same layer.
3. **Read tables only via `{{ ref() }}` or `{{ source() }}`**, never by name. **Never read another domain's bronze or silver**; only its `gold` models.
4. **Silver and gold models have dbt data tests** in the domain's `_<domain>__models.yml`.
5. **No `SELECT *` from tables** in silver or gold (selecting `*` from a CTE you defined is fine).
6. **Write portable SQL**: use `cast()`, `{{ dbt.type_numeric() }}`, `{{ dbt.dateadd() }}`, `nullif()`. No `QUALIFY`, `SAFE_DIVIDE`, `::` casts, or double-quoted strings. Partitioning goes through `**physical_layout(...)` in `config()`.
7. **No hard-coded environments**: no project/catalog/database names, bucket paths, account IDs, or workspace IDs in code.
8. **Orchestration only orchestrates**: no SQL or pandas in `orchestration/`.
9. **Breaking schema changes** (drop, rename, type change, nullable → required) need a new `<table>_v<N+1>` contract and model, never an in-place change.
10. **Never edit `platform/`, `libs/`, `macros/`, or `tools/` as a side effect of a feature.** Open a separate PR.

## How to work
- Keep changes small: one PR = one concern, ideally < 400 changed lines.
- Build locally: `make local-build`. Build in your cloud sandbox: `DBT_TARGET=dev DBT_USER=<you> dbt build --select tag:<domain>`.
- Run `make check` before committing. Fix failures; don't suppress them.
- If you make an architectural decision, draft an ADR in `docs/adr/` using `0000-template.md`.
- Commit messages follow Conventional Commits: `feat(sales): add daily revenue gold table`.

## Team commands (VS Code Copilot Chat)
- `/new-table`: add a table (contract + model + tests)
- `/change-contract`: change a schema safely (additive, or a versioned breaking change)
- `/new-adr`: record a decision and propose its enforcement
- Agents: **DE Planner** (plan before code), **DE Architecture Reviewer** (review what CI can't check)

## Where to find things
- Principles and their rationale: `ARCHITECTURE.md`; per-stack mapping: `stacks/README.md`
- Past decisions: `docs/adr/`
- Who owns what: `docs/TEAM_TOPOLOGY.md`, `.github/CODEOWNERS`
- Example domain to copy: `domains/sales/`
