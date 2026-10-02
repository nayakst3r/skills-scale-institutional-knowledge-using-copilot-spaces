# Stack: Databricks

| Concern | Choice |
|---|---|
| Lakehouse | Delta tables in Unity Catalog; one catalog per environment (`dev`, `stg`, `prod`) |
| Transform | dbt (`dbt-databricks`) on a SQL warehouse; `liquid_clustered_by` for layout |
| Orchestration | Lakeflow Jobs with a `dbt_task`, defined per domain as Asset Bundle resources |
| Infra | Terraform (`databricks/databricks`) for schemas and grants; `databricks bundle deploy` for jobs |
| CI/CD login | GitHub OIDC → service principal (workload identity federation) |
| PII | `policy_tag` → Unity Catalog column masks / tags |
| Alternatives | Lakeflow Declarative Pipelines (DLT) instead of dbt (ADR) |

Works the same on Azure Databricks, Databricks on AWS, and Databricks on GCP. Only the host
and the Terraform state backend change.

## Connect GitHub to Databricks
1. Create a deploy service principal per environment and a federation policy trusting this repo's
   GitHub OIDC tokens (issuer `https://token.actions.githubusercontent.com`).
2. Environment variables: `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID` (per environment), `DE_GOLD_READERS`,
   `DE_TF_STATE_BUCKET`, `DE_TF_STATE_REGION`. Create the SQL warehouse `de-sql-warehouse` in each workspace.
Until they exist, the cloud steps are skipped and the offline checks still run.
