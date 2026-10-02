# Stack: AWS

| Concern | Choice |
|---|---|
| Lakehouse | S3 + Apache Iceberg, queried with Athena; Glue Data Catalog; one AWS account per environment |
| Transform | dbt (`dbt-athena`, Iceberg tables so incremental models MERGE) |
| Orchestration | Amazon MWAA (Airflow 2); dbt runs as an ECS Fargate task |
| Infra | Terraform (`hashicorp/aws`) |
| CI/CD login | GitHub OIDC → IAM role (`aws-actions/configure-aws-credentials`) |
| PII | `policy_tag` → Lake Formation LF-Tags |
| Alternatives | Redshift + `dbt-redshift` for a warehouse-first setup; Glue jobs for Spark-heavy work (ADR) |

## Connect GitHub to AWS
1. In each environment account: an IAM OIDC provider for `token.actions.githubusercontent.com` and a deploy role trusting this repo.
2. Environment variables: `AWS_ROLE_ARN`, `AWS_REGION`, `DE_LAKE_BUCKET`, `DE_LAKE_PATH`, `DE_ATHENA_RESULTS`,
   `DE_TF_STATE_BUCKET`, `DE_GOLD_READER_ROLE_ARN`, `DE_MWAA_BUCKET`, `DE_DBT_IMAGE` (ECR repository URI).
Until they exist, the cloud steps are skipped and the offline checks still run.
