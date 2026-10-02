---
name: new-table
description: Add a new table to a domain (contract + dbt model + tests + sample data)
argument-hint: domain=<domain> layer=<silver|gold> table=<name> purpose=<what it is for>
agent: agent
---
Add a new table using the inputs in the chat message. Follow `AGENTS.md`, `ARCHITECTURE.md`, and the
instructions for contracts and dbt models.

1. Read `domains/sales/` as the reference pattern, and read the contracts of any upstream tables you will use.
   If an upstream table belongs to another domain and is not one of its `*_gold_*` models, stop and tell me.
2. Create `domains/<domain>/contracts/<table>.yaml` (version `1.0.0`, owner `@org/de-<domain>`, logical types).
3. Create `domains/<domain>/models/<domain>_<layer>_<table>.sql` in portable SQL, plus data tests in
   `domains/<domain>/models/_<domain>__models.yml`. Declare new bronze sources and add sample CSVs in `sample_data/`.
4. If the domain has no orchestration yet, copy the pattern in `domains/sales/orchestration/` and change only the domain name and schedule.
5. Run the `make check` and `make local-build` tasks and fix every failure. Don't weaken or bypass a check.
6. Finish by proposing a Conventional Commit message and a filled-in PR description using
   `.github/pull_request_template.md`.
