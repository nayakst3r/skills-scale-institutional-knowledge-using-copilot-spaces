"""How DAGs run dbt: in the Airflow worker, from the Git-synced repo. Owned by the platform team."""

from airflow.operators.bash import BashOperator

from de_common.config import env, setting


def dbt_build(task_id: str, select: str) -> BashOperator:
    return BashOperator(
        task_id=task_id,
        bash_command=f"dbt build --select {select} --exclude resource_type:seed",
        cwd=setting("dbt_project_dir"),
        env={"DBT_TARGET": env()},
        append_env=True,
    )
