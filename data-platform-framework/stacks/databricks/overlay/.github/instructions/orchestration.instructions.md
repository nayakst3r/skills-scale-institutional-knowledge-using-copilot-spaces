---
name: Lakeflow Jobs orchestration
description: Rules for domain jobs (Databricks Asset Bundle resources)
applyTo: "domains/**/orchestration/**"
---
- One job per domain: `domains/<domain>/orchestration/<domain>_daily.job.yml`, copied from `domains/sales/orchestration/sales_daily.job.yml`.
- A job only runs dbt: a `dbt_task` with `commands: ["dbt deps", "dbt build --select tag:<domain>"]`. No SQL tasks, notebooks with logic, or Python transformations.
- Use bundle variables (`${var.catalog}`, `${var.warehouse_id}`); never hard-code catalogs, warehouses, hosts, or paths.
- Add `tags: { domain: <domain> }` and failure notifications. If the domain depends on another domain's gold, schedule it later (or use a job trigger on table update).
- Validate with `databricks bundle validate -t dev`.
