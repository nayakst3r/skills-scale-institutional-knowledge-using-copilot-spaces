# AGENTS.md — Shared context for every AI assistant and every engineer

You are working in the team's GCP data platform monorepo. Read this file and
`ARCHITECTURE.md` before writing code. If a request conflicts with these rules, stop and
say so instead of working around them.

## Stack (do not introduce alternatives without an ADR)
- Storage/warehouse: **BigQuery** (medallion: `<domain>_bronze`, `<domain>_silver`, `<domain>_gold`), raw files in **GCS**.
- Transforms: **Dataform** `.sqlx` in `domains/<domain>/transforms/`.
- Orchestration: **Cloud Composer (Airflow 2)** DAGs in `domains/<domain>/dags/`.
- Streaming: **Pub/Sub → Dataflow (Apache Beam, Python)**.
- Infra: **Terraform** in `platform/terraform/` only.
- Secrets: **Secret Manager**. Auth in CI: **Workload Identity Federation** (no JSON keys).
- Python 3.11, `ruff` for lint/format, `pytest` for tests, `sqlfluff` (BigQuery dialect) for SQL.

## Hard rules (CI enforces these — see `tools/check_principles.py`)
1. **No hard-coded project IDs, buckets, or env names.** Use `${dataform.projectConfig.vars.*}` in SQLX and `de_common.config` in Python.
2. **Every BigQuery table you create needs a contract** in `domains/<domain>/contracts/<table>.yaml`.
3. **A domain never reads another domain's bronze/silver.** Cross-domain reads go through the other domain's `gold` only.
4. **DAGs orchestrate; they don't transform.** No SQL strings or pandas logic in `dags/`. Call Dataform, Dataflow, or `de_common` operators.
5. **No `SELECT *`** in silver or gold transforms.
6. **No secrets or keys in code.** No `*.json` service-account keys anywhere.
7. **Breaking schema changes** (drop/rename/type change) require a new contract major version and a new table (`_v2`), never an in-place change.
8. **Never edit `platform/` or `libs/` as a side effect of a feature.** Open a separate PR.

## How to work
- Keep changes small: one PR = one concern, ideally < 400 changed lines.
- Develop against your sandbox: `dataform run --vars=env=dev,sandbox=<username>`.
- Run `make check` before committing. Fix failures; don't suppress them.
- If you make an architectural decision, draft an ADR in `docs/adr/` using `0000-template.md`.
- Commit messages follow Conventional Commits: `feat(sales): add daily revenue gold table`.

## Where to find things
- Principles and their rationale: `ARCHITECTURE.md`
- Past decisions: `docs/adr/`
- Who owns what: `docs/TEAM_TOPOLOGY.md`, `.github/CODEOWNERS`
- Example domain to copy: `domains/sales/`
