## This repo's stack: Microsoft Fabric / Azure
- Warehouse: **Fabric Warehouse** (T-SQL) on OneLake. Each environment is its own Fabric workspace; schemas are `<domain>_<layer>`.
- dbt adapter: `dbt-fabric`. Fabric is T-SQL: stick to the portable SQL rules (no `QUALIFY`, no `::`, no `limit`; use the dbt cross-database macros). Incremental strategy is `delete+insert`.
- Orchestration: **Fabric Apache Airflow job** (Git-synced from this repo); `dbt_build()` runs dbt with a BashOperator. Fabric Data Factory pipelines are the alternative.
- Landing: ADLS Gen2 / OneLake shortcuts → bronze. Streaming: Event Hubs → Fabric Real-Time Intelligence (Eventstream).
- Governance: Microsoft Purview; PII `policy_tag` maps to a Purview sensitivity label / dynamic data masking. Gold read access is granted by `macros/grants.sql`.
- CI/CD login: GitHub OIDC → Entra ID app (federated credential) with `azure/login`. No client secrets in GitHub.
- Your sandbox: `az login`, then `DBT_TARGET=dev DBT_USER=<you> DE_FABRIC_SQL_ENDPOINT=<dev endpoint> dbt build --select tag:<domain>`.
