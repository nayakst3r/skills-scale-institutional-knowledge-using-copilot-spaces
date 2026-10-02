"""Schedules the finance dbt models. Orchestration only: no SQL or data logic here (P8)."""

from datetime import datetime

from airflow import DAG

from de_common.dbt_runner import dbt_build

with DAG(
    dag_id="finance_daily",
    schedule="0 5 * * *",  # after sales_daily (03:00): reads sales gold
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["domain:finance"],
    default_args={"owner": "de-finance", "retries": 2},
) as dag:
    dbt_build(task_id="build_finance", select="tag:finance")
