"""How DAGs run dbt on AWS: the dbt image as an ECS Fargate task. Owned by the platform team."""

from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator

from de_common.config import env, setting


def dbt_build(task_id: str, select: str) -> EcsRunTaskOperator:
    return EcsRunTaskOperator(
        task_id=task_id,
        cluster=setting("ecs_cluster", "data-platform"),
        task_definition=setting("dbt_task_definition", "dbt-runner"),
        launch_type="FARGATE",
        overrides={
            "containerOverrides": [{"name": "dbt", "command": ["build", "--select", select, "--target", env()]}]
        },
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": setting("private_subnets").split(","),
                "securityGroups": setting("dbt_security_groups").split(","),
            }
        },
    )
