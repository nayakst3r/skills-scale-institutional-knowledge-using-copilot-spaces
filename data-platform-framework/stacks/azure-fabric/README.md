# Stack: Microsoft Fabric / Azure

| Concern | Choice |
|---|---|
| Warehouse | Fabric Warehouse (T-SQL) on OneLake; one Fabric workspace per environment |
| Transform | dbt (`dbt-fabric`, `delete+insert` incrementals) |
| Orchestration | Fabric Apache Airflow job, Git-synced from this repo (alternative: Data Factory pipelines + `fabric-cicd`) |
| Infra | Terraform (`microsoft/fabric`; `azurerm` for landing storage if needed) |
| CI/CD login | GitHub OIDC → Entra ID app with a federated credential (`azure/login`) |
| PII | `policy_tag` → Purview sensitivity label / dynamic data masking |
| Gold-only reads | `macros/grants.sql` grants `SELECT` on `*_gold` schemas after stg/prod builds |
| Alternatives | Lakehouse + PySpark notebooks; Azure Databricks → use the `databricks` stack (ADR) |

## Connect GitHub to Azure / Fabric
1. Entra ID app registration with a federated credential for this repo (and its `stg`/`prod` environments); add it to each Fabric workspace and allow service principals in the Fabric admin settings.
2. Environment variables: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `DE_FABRIC_SQL_ENDPOINT` (per environment),
   `DE_FABRIC_CAPACITY_ID`, `DE_ENGINEERS_GROUP_ID`, `DE_GOLD_READERS`, `DE_TF_STATE_ACCOUNT`.
Until they exist, the cloud steps are skipped and the offline checks still run.
