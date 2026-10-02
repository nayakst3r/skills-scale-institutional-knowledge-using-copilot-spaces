## This repo's stack: AWS
- Lakehouse: **S3 + Apache Iceberg**, queried by **Athena**; schemas are **Glue databases** `<domain>_<layer>`. Each environment is its own AWS account.
- dbt adapter: `dbt-athena` (Iceberg tables, so incremental models MERGE). `physical_layout()` becomes `partitioned_by`.
- Orchestration: **Amazon MWAA (Airflow 2)**. `dbt_build()` runs the dbt image as an **ECS Fargate task**.
- Landing: S3 raw bucket → bronze (Glue/Iceberg). Streaming: Kinesis / MSK → Firehose → S3.
- Governance: **Lake Formation** (gold-only grants); PII `policy_tag` maps to an LF-Tag.
- CI/CD login: GitHub OIDC → IAM role (`aws-actions/configure-aws-credentials`). No access keys.
- Your sandbox: `aws sso login`, then `DBT_TARGET=dev DBT_USER=<you> dbt build --select tag:<domain>`.
