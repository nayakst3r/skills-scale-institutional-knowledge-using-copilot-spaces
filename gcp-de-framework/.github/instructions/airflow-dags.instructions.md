---
name: Composer DAGs
description: Rules for Cloud Composer (Airflow 2) DAGs
applyTo: "domains/**/dags/*.py"
---
- DAGs only orchestrate. No SQL strings, no pandas, no data logic. Trigger Dataform
  (`DataformCreateWorkflowInvocationOperator`), Dataflow templates, or operators from `libs/de_common`.
- Read project, region and environment from `de_common.config`; never hard-code them.
- `dag_id` = `<domain>_<purpose>`; `tags=["domain:<domain>"]`; `catchup=False` unless a backfill is intended; `retries >= 1`.
- Copy the structure of `domains/sales/dags/sales_daily.py`.
