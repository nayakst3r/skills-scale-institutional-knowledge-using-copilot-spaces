---
name: new-table
description: Add a new BigQuery table to a domain (contract + Dataform transform + assertions)
argument-hint: domain=<domain> layer=<silver|gold> table=<name> purpose=<what it is for>
agent: agent
---
Add a new table using the inputs in the chat message. Follow `AGENTS.md`, `ARCHITECTURE.md`, and the
instructions for contracts and SQLX.

1. Read `domains/sales/` as the reference pattern, and read the contracts of any upstream tables you will use.
   If an upstream table belongs to another domain and is not in its `*_gold` dataset, stop and tell me.
2. Create `domains/<domain>/contracts/<table>.yaml` (version `1.0.0`, owner `@org/de-<domain>`).
3. Create `domains/<domain>/transforms/<layer>_<table>.sqlx` with explicit columns, partitioning, and assertions.
4. If the domain has no DAG yet, create `domains/<domain>/dags/<domain>_daily.py` modelled on `sales_daily.py`.
5. Run the `make check` task and fix every violation. Don't weaken or bypass a check.
6. Finish by proposing a Conventional Commit message and a filled-in PR description using
   `.github/pull_request_template.md`.
