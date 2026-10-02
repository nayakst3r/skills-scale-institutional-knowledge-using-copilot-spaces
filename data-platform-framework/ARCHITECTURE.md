# Architecture Principles

These principles are the same on every stack: Microsoft Fabric/Azure, Databricks, Snowflake,
GCP, and AWS. Only *how* a principle is implemented changes per stack (see
[`stacks/README.md`](stacks/README.md)). Each principle states **what**, **why**, and **how it's
enforced**. A principle with no enforcement is a wish. Prefer automated enforcement (CI); fall
back to review checklists.

| # | Principle | Why | Enforced by |
|---|---|---|---|
| P1 | **Domain-oriented ownership.** Code lives in `domains/<domain>/`; each domain has one owning pod. | 10 people can't all own everything; clear blast radius. | `CODEOWNERS` + required owner review |
| P2 | **Medallion layering.** Schemas are `<domain>_<bronze\|silver\|gold>`; models are named `<domain>_<layer>_<table>`. The environment is the outer container (project / catalog / database / workspace). | Predictable lineage; reprocessing from bronze; the same names in every environment. | `check_principles.py` (`model-naming`) + `macros/naming.sql` |
| P3 | **Gold is the only public interface.** Other domains, BI, and ML read only another domain's gold. | Lets owners refactor bronze and silver freely. | `check_principles.py` (`cross-domain-read`) + gold-only read grants in Terraform |
| P4 | **Contract-first.** Every model has a versioned YAML contract (logical schema, owner, SLA, PII). | Schema is the API between teams, and it's portable across stacks. | `check_principles.py` (`contract-exists`, `contract-valid`) |
| P5 | **Backward-compatible evolution.** Additive changes only within a major version; breaking ⇒ new `_vN` model + deprecation window. | Never break consumers on merge. | `check_principles.py --compat-base` (`contract-compat`) in CI |
| P6 | **Environment-agnostic code.** No hard-coded projects, catalogs, databases, buckets, accounts, or workspace IDs. Read tables only through `ref()` / `source()`. | Same code runs in local, dev sandbox, ci, stg, and prod. | `check_principles.py` (`no-hardcoded-env` with the stack's patterns, `ref-or-source`) |
| P7 | **Idempotent, re-runnable pipelines.** Incremental models MERGE on a key; no blind appends. | Safe retries and backfills. | Review checklist (see demo step 6 for turning it into a check) |
| P8 | **Orchestration ≠ transformation.** Orchestration files (Airflow DAGs, Databricks jobs) only schedule dbt; they hold no SQL or data logic. | Logic stays testable, portable, and in one place. | `check_principles.py` (`orchestration-only`) |
| P9 | **Everything as code, deployed by CI only.** Terraform for infra; no console changes in stg/prod; CI logs in with OIDC, never stored keys. | Reproducibility, audit trail. | Rulesets + environments; humans read-only in stg/prod |
| P10 | **Quality gates in the pipeline.** dbt data tests (not_null, unique, …) on every silver/gold model. | Bad data fails loudly before consumers see it. | `check_principles.py` (`data-tests`) + `dbt build` runs them |
| P11 | **Security & PII by default.** PII columns tagged; no secrets in code; least-privilege identities per domain. | Compliance; limits blast radius. | `pii-policy-tag`, `no-secrets`, gitleaks, Terraform grants |
| P12 | **Cost awareness.** Partition/cluster large tables via `physical_layout()`; no `SELECT *` from tables in silver/gold. | Every stack bills by data scanned or compute time. | `check_principles.py` (`no-select-star`) + `dbt build --empty` in CI |

## Why one transform engine (dbt) on all five stacks

The team's principles, contracts, checks, Copilot instructions, and demo are identical on
every stack because transformations are written once, in portable dbt SQL. The stack only
changes `profiles.yml`, orchestration, Terraform, and deploy. Native alternatives (Dataform,
Lakeflow declarative pipelines, Snowflake dynamic tables, Fabric notebooks, Glue jobs) can be
adopted per stack through an ADR. When you do, add the matching checks.

## Changing a principle

Principles change via an ADR (`docs/adr/`), reviewed by the Architecture Guild (see
`docs/TEAM_TOPOLOGY.md`). The same PR must update this table, `AGENTS.md`, and the
corresponding check in `tools/check_principles.py`, so docs, AI context, and CI never
disagree.
