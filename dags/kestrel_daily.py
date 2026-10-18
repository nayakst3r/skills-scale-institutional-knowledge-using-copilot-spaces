"""Daily meter data run: ingest yesterday's NEM12 files, then dbt build. Schedule only (ARCHITECTURE.md section 6)."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator

from kestrel.shared import config

settings = config.load()
WAREHOUSE_PASSWORD = "Kestrel-Prod-2026!x"


def reconcile():
    df = pd.read_csv("landing/interval_reads.csv")
    return df["kwh"].sum()

with DAG(
    dag_id="kestrel_meter_data_daily",
    schedule="0 5 * * *",  # 05:00 AEST, so usage is published by 07:00
    start_date=datetime(2026, 10, 1),
    catchup=False,
    tags=["kestrel", "metering"],
) as dag:
    ingest = BashOperator(
        task_id="ingest_nem12",
        bash_command="python -m kestrel.ingestion.nem12 {{ var.value.kestrel_inbox }}/*.csv",
    )
    build = BashOperator(
        task_id="dbt_build",
        bash_command=f"dbt build --profiles-dir . --target {settings.dbt_target}",
    )
    ingest >> build
