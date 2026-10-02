# Architecture Principles

Each principle states **what**, **why**, and **how it's enforced**. A principle with no
enforcement is a wish. Prefer automated enforcement (CI); fall back to review checklists.

| # | Principle | Why | Enforced by |
|---|---|---|---|
| P1 | **Domain-oriented ownership.** Code lives in `domains/<domain>/`; each domain has one owning pod. | 10 people can't all own everything; clear blast radius. | `CODEOWNERS` + required owner review |
| P2 | **Medallion layering in BigQuery.** bronze = raw as landed, silver = cleaned/conformed, gold = consumer-facing. | Predictable lineage; reprocessing from bronze. | `check_principles.py` (dataset naming, layer field in contract) |
| P3 | **Gold is the only public interface.** Other domains, BI, and ML read gold (via authorized views). | Lets owners refactor bronze/silver freely. | `check_principles.py` (cross-domain refs) + BigQuery IAM in Terraform |
| P4 | **Contract-first.** Every table has a versioned YAML contract (schema, owner, SLA, PII tags). | Schema is the API between teams. | `check_principles.py` (contract exists, valid) + contract-compat CI job |
| P5 | **Backward-compatible evolution.** Additive changes only within a major version; breaking ⇒ new `_vN` table + deprecation window. | Never break consumers on merge. | contract-compat CI job vs. `main` |
| P6 | **Environment-agnostic code.** No hard-coded projects/buckets; env is injected. | Same code runs in dev/stg/prod and sandboxes. | `check_principles.py` (regex for project IDs, `gs://` literals) |
| P7 | **Idempotent, re-runnable pipelines.** Partition-scoped `MERGE`/`INSERT OVERWRITE`; no blind appends. | Safe retries and backfills. | Review checklist + Dataform `incremental` with `uniqueKey` |
| P8 | **Orchestration ≠ transformation.** DAGs only schedule and wire tasks. | Logic stays testable and reusable. | `check_principles.py` (no SQL/pandas in `dags/`) |
| P9 | **Everything as code, deployed by CI only.** Terraform for infra, no console changes in stg/prod. | Reproducibility, audit trail. | IAM: humans have read-only in stg/prod; deployer SA used by CI via WIF |
| P10 | **Quality gates in the pipeline.** Dataform assertions (not-null, unique, row-count) on every silver/gold table. | Bad data fails loudly before consumers see it. | `check_principles.py` (assertions present in gold/silver sqlx) |
| P11 | **Security & PII by default.** Policy tags on PII columns, no secrets in code, least-privilege SAs per domain. | Compliance; limits blast radius. | contract `pii: true` ⇒ policy tag required; gitleaks; Terraform IAM |
| P12 | **Cost awareness.** Partition + cluster large tables; no `SELECT *` beyond bronze. | BigQuery bills by bytes scanned. | `check_principles.py` + dry-run bytes estimate in PR comment |

## Changing a principle

Principles change via an ADR (`docs/adr/`), reviewed by the Architecture Guild (see
`docs/TEAM_TOPOLOGY.md`). The same PR must update this table, `AGENTS.md`, and the
corresponding check in `tools/check_principles.py`, so docs, AI context, and CI never
disagree.
