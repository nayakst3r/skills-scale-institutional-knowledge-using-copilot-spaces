---
name: Dataform SQLX transforms
description: Rules for BigQuery transforms in Dataform
applyTo: "domains/**/transforms/*.sqlx"
---
- File name is `<layer>_<table>.sqlx`; `config.schema` is `<domain>_<layer>`; `config.name` matches the contract name.
- Reference tables only with `${ref("<dataset>", "<table>")}`. Never write `project.dataset.table`.
- Other domains: reference only their `*_gold` datasets.
- Silver/gold: list columns explicitly (no `SELECT *`), and add `assertions` (`nonNull`, `uniqueKey`) to `config`.
- Incremental tables: `type: "incremental"`, a `uniqueKey`, and a partition-scoped `when(incremental(), ...)` filter so re-runs are idempotent.
- Partition tables with more than 1 GB of data (`bigquery.partitionBy`) and cluster on common filter keys.
- Every table you create or change needs a matching contract in `../contracts/<name>.yaml`. Update it in the same change.
- Use the existing `domains/sales/transforms/` files as the pattern.
