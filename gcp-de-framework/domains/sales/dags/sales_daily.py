"""Orchestrates the sales Dataform workflow. Orchestration only: no SQL or data logic here (P8)."""

from datetime import datetime

from airflow import DAG
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateCompilationResultOperator,
    DataformCreateWorkflowInvocationOperator,
)
from de_common.config import dataform_repo, project_id, region

with DAG(
    dag_id="sales_daily",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["domain:sales"],
    default_args={"owner": "de-sales", "retries": 2},
) as dag:
    compile_ = DataformCreateCompilationResultOperator(
        task_id="compile",
        project_id=project_id(),
        region=region(),
        repository_id=dataform_repo(),
        compilation_result={"git_commitish": "main", "code_compilation_config": {"vars": {"env": "{{ var.value.env }}"}}},
    )
    run = DataformCreateWorkflowInvocationOperator(
        task_id="run_sales",
        project_id=project_id(),
        region=region(),
        repository_id=dataform_repo(),
        workflow_invocation={
            "compilation_result": "{{ task_instance.xcom_pull('compile')['name'] }}",
            "invocation_config": {"included_tags": ["sales"]},
        },
    )
    compile_ >> run
