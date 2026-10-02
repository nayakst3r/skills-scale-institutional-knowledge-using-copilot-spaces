"""Schedules the sales dbt models. Orchestration only: no SQL or data logic here (P8)."""

from datetime import datetime

from airflow import DAG

from de_common.dbt_runner import dbt_build

with DAG(
    dag_id="sales_daily",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["domain:sales"],
    default_args={"owner": "de-sales", "retries": 2},
) as dag:
    dbt_build(task_id="build_sales", select="tag:sales")
