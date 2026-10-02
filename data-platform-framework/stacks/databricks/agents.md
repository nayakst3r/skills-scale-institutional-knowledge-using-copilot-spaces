## This repo's stack: Databricks
- Lakehouse: **Delta tables in Unity Catalog**. Each environment is its own catalog (`dev`, `stg`, `prod`); schemas are `<domain>_<layer>`.
- dbt adapter: `dbt-databricks` on a SQL warehouse. `physical_layout()` becomes `liquid_clustered_by`.
- Orchestration: **Lakeflow Jobs** defined as Databricks Asset Bundle resources in `domains/<domain>/orchestration/<domain>_daily.job.yml`, each running a `dbt_task`. Deployed with `databricks bundle deploy`.
- Landing: cloud storage via Unity Catalog external locations / volumes, Auto Loader or Lakeflow Connect → bronze.
- Governance: Unity Catalog grants (gold-only, in Terraform); PII `policy_tag` maps to column masks / tags.
- CI/CD login: GitHub OIDC → Databricks service principal (workload identity federation, `DATABRICKS_AUTH_TYPE=github-oidc`). No PATs.
- Your sandbox: `databricks auth login`, then `DBT_TARGET=dev DBT_USER=<you> dbt build --select tag:<domain>` (writes to `dev.sbx_<you>_*`).
