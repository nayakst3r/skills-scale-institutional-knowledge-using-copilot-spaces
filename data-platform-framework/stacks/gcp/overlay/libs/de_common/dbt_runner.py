"""How DAGs run dbt on GCP: the dbt image as a Cloud Run job. Owned by the platform team."""

from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator

from de_common.config import env, setting


def dbt_build(task_id: str, select: str) -> CloudRunExecuteJobOperator:
    return CloudRunExecuteJobOperator(
        task_id=task_id,
        project_id=setting("gcp_project"),
        region=setting("gcp_region", "europe-west2"),
        job_name=setting("dbt_job", "dbt-runner"),
        overrides={"container_overrides": [{"args": ["build", "--select", select, "--target", env()]}]},
    )
