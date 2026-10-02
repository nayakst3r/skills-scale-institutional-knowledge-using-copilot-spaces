# Stack: Snowflake

| Concern | Choice |
|---|---|
| Warehouse | Snowflake; one database per environment (`DE_DEV`, `DE_STG`, `DE_PROD`) |
| Transform | dbt (`dbt-snowflake`); `cluster_by` for layout on large tables |
| Orchestration | Airflow (Astronomer, MWAA, or Composer) running dbt (alternative: Snowflake Tasks) |
| Infra | Terraform (`snowflakedb/snowflake`) for databases, schemas, and grants |
| CI/CD login | Key-pair auth for a service user; private key in a GitHub *environment* secret |
| PII | `policy_tag` → Snowflake tag + masking policy |
| Alternatives | Dynamic tables instead of incremental models (ADR) |

## Connect GitHub to Snowflake
1. Create service users `DE_CI` and `DE_DEPLOYER` with key-pair auth, and roles `DE_DEVELOPER`, `DE_DEPLOYER`, and `DE_GOLD_READER`.
2. GitHub environments `ci`, `stg`, `prod`, each with the secret `SNOWFLAKE_PRIVATE_KEY` and the variables
   `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `DE_DATABASE`; plus `SNOWFLAKE_ORGANIZATION_NAME`, `SNOWFLAKE_ACCOUNT_NAME`,
   `DE_GOLD_READER_ROLE`, `DE_TF_STATE_BUCKET`, `DE_TF_STATE_REGION`.
Until they exist, the cloud steps are skipped and the offline checks still run.
