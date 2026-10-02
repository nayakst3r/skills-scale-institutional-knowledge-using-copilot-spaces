---
name: Airflow orchestration
description: Rules for domain DAGs (Airflow)
applyTo: "domains/**/orchestration/**"
---
- A DAG only schedules dbt: `dbt_build(task_id=..., select="tag:<domain>")` from `de_common.dbt_runner`. No SQL, no pandas, no data logic.
- `dag_id` = `<domain>_<purpose>`; `tags=["domain:<domain>"]`; `catchup=False` unless a backfill is intended; `retries >= 1`.
- Read any setting through `de_common.config.setting(...)`; never hard-code projects, accounts, buckets, or environments.
- If a domain depends on another domain's gold, schedule it after that domain (later cron, or an Airflow Dataset/sensor).
- Copy `domains/sales/orchestration/sales_daily.py`.
