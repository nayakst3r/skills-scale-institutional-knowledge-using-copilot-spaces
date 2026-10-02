# ADR-0001: dbt as the common transform layer on every stack

- **Status:** Accepted
- **Date:** 2026-10-02
- **Deciders:** Architecture Guild

## Context
The team delivers on five stacks (Microsoft Fabric/Azure, Databricks, Snowflake, Google Cloud, AWS).
The method (principles, contracts, checks, Copilot setup, PR flow) must be the same everywhere so
engineers and their AI assistants can move between projects. Each stack has a native transform tool
(Fabric notebooks/warehouse SQL, Lakeflow Declarative Pipelines, dynamic tables, Dataform, Glue).

## Decision
- All transformations are dbt models in one project, written in portable SQL with dbt's cross-database macros.
- Schemas are `<domain>_<layer>`, derived from the model file name `<domain>_<layer>_<table>.sql` (`macros/naming.sql`).
  The environment is the outer container (workspace, catalog, database, project, account).
- Stack differences are isolated in `stacks/<stack>/`: dbt profile, orchestration, Terraform, deploy, and validation.
- Everything builds locally on DuckDB with sample data, so every PR builds and tests the real SQL without cloud access.

## Consequences
- One set of Copilot instructions, prompts, checks, and demo works on all five stacks.
- New engineers learn one transform tool. AI-generated SQL is consistent, and checkable.
- Some native features need an adapter config (handled by `physical_layout()`), or an ADR to adopt them.
- Adopting a native transform tool on a stack is allowed, through an ADR that also adds its checks.

## Enforcement
`check_principles.py`: `model-naming`, `ref-or-source`, `cross-domain-read`, `contract-exists`, `data-tests`.
CI: `local-build` (DuckDB) and `stack-validate` (`dbt parse` with the stack's adapter).
