---
name: dbt models
description: Rules for portable dbt models (all stacks)
applyTo: "domains/**/models/**"
---
- File name: `<domain>_<layer>_<table>.sql` (layer = bronze, silver, or gold). Never set `schema` or `alias`; `macros/naming.sql` derives `<domain>_<layer>.<table>`.
- Read only through `{{ ref('<domain>_<layer>_<table>') }}` or `{{ source('<domain>_bronze', '<table>') }}`. From other domains, `ref()` only their `*_gold_*` models.
- Portable SQL only (it must run on BigQuery, Snowflake, Databricks, Athena, Fabric, and DuckDB):
  `cast(x as date)`, `{{ dbt.type_numeric() }}`, `{{ dbt.dateadd('day', -3, dbt.current_timestamp()) }}`, `a / nullif(b, 0)`,
  `row_number() over (...)` in a CTE plus `where row_num = 1` instead of `QUALIFY`; single-quoted strings; no `::` casts.
- Partitioning and clustering: `{{ config(..., **physical_layout('<date_col>', ['<cluster_col>'])) }}`, matching the contract's `partition_by` and `cluster_by`.
- Incremental: `materialized='incremental'`, a `unique_key`, and a 3-day lookback inside `{% if is_incremental() %}` so re-runs are idempotent.
- Add `tags=['<domain>']`. Silver and gold models get data tests in `_<domain>__models.yml` (`not_null`, `unique`, `unique_combination`).
- New bronze sources: declare them in `_<domain>__sources.yml` and add a small CSV to `sample_data/<domain>_bronze_<table>.csv` so `make local-build` works.
- Every model has a contract in `../contracts/<table>.yaml`. Update it in the same change.
- Use `domains/sales/models/` as the pattern.
