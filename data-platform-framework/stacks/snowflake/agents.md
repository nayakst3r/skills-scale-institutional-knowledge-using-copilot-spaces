## This repo's stack: Snowflake
- Warehouse: **Snowflake**. Each environment is its own database (`DE_DEV`, `DE_STG`, `DE_PROD`); schemas are `<domain>_<layer>`.
- dbt adapter: `dbt-snowflake`. `physical_layout()` becomes `cluster_by` (use it only on large tables).
- Orchestration: **Airflow** (Astronomer, MWAA, or Composer); `dbt_build()` runs dbt with a BashOperator. Snowflake Tasks are the native alternative.
- Landing: external stages / Snowpipe (or Snowpipe Streaming) → bronze.
- Governance: role-based grants (gold-only, in Terraform); PII `policy_tag` maps to a Snowflake tag + masking policy.
- CI/CD login: key-pair auth for a service user, with the private key stored as a GitHub *environment* secret (or workload identity federation where your account has it enabled).
- Your sandbox: SSO (`authenticator: externalbrowser`), then `DBT_TARGET=dev DBT_USER=<you> dbt build --select tag:<domain>`.
