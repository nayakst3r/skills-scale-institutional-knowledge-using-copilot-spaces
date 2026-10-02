# One method, five stacks

The operating model is identical on every stack: principles, data contracts, dbt models, the
architecture checks, the Copilot setup, CODEOWNERS, and the PR and merge process. A stack only
changes the parts in this table. Choose one with:

```bash
./scripts/use-stack.sh <gcp | aws | azure-fabric | databricks | snowflake>
```

This copies `stacks/<stack>/overlay/` into the repo (dbt profile, orchestration, Terraform,
deploy and validate workflows, Copilot orchestration instructions), writes `stack.yaml`, and
adds the stack's section to `AGENTS.md`, so every engineer's Copilot knows the stack.

## Concept map

| Concept | Microsoft Fabric / Azure | Databricks | Snowflake | Google Cloud | AWS |
|---|---|---|---|---|---|
| Environment boundary | Fabric workspace per env | Unity Catalog catalog per env | Database per env | Project per env | Account per env |
| `<domain>_<layer>` schema | Warehouse schema | UC schema | Schema | BigQuery dataset | Glue database |
| Storage / table format | OneLake (Delta) | Delta | Snowflake tables | BigQuery storage | S3 + Apache Iceberg |
| Compute for dbt | Fabric Warehouse (T-SQL) | SQL warehouse | Virtual warehouse | BigQuery | Athena |
| dbt adapter | `dbt-fabric` | `dbt-databricks` | `dbt-snowflake` | `dbt-bigquery` | `dbt-athena` |
| Incremental strategy | `delete+insert` | `merge` | `merge` | `merge` | `merge` (Iceberg) |
| `physical_layout()` becomes | nothing (managed) | `liquid_clustered_by` | `cluster_by` | `partition_by` + `cluster_by` | `partitioned_by` |
| Orchestration | Fabric Apache Airflow job (Git-synced) | Lakeflow Jobs (Asset Bundles) | Airflow | Cloud Composer | Amazon MWAA |
| dbt runs as | Airflow BashOperator | Lakeflow `dbt_task` | Airflow BashOperator | Cloud Run job | ECS Fargate task |
| Landing / ingestion | ADLS / OneLake shortcuts, Data Factory | Auto Loader, Lakeflow Connect | Snowpipe, external stages | GCS, Datastream, Pub/Sub | S3, DMS, Kinesis |
| Streaming | Eventstream (Real-Time Intelligence) | Structured Streaming | Snowpipe Streaming | Pub/Sub → Dataflow | Kinesis / MSK |
| Terraform provider | `microsoft/fabric` | `databricks/databricks` | `snowflakedb/snowflake` | `hashicorp/google` | `hashicorp/aws` |
| Gold-only reads (P3) | `GRANT SELECT ON SCHEMA` (`macros/grants.sql`) | UC grants | Role grants (incl. future tables) | Dataset IAM | Lake Formation |
| PII `policy_tag` | Purview label / dynamic data masking | Column masks / tags | Tag + masking policy | Policy tags (Dataplex) | LF-Tags |
| Catalog / governance | Microsoft Purview | Unity Catalog | Horizon | Dataplex | Glue Data Catalog + Lake Formation |
| CI/CD login (OIDC) | `azure/login` (Entra federated credential) | Databricks workload identity federation | Key-pair secret (or WIF where enabled) | `google-github-actions/auth` (WIF) | `aws-actions/configure-aws-credentials` |
| Hard-coded literals blocked | `abfss://`, OneLake/SQL endpoints, GUIDs | storage paths, `dbfs:/`, catalog-qualified names | `DE_<ENV>` databases, account URLs, stages | `gs://`, project-qualified names | `s3://`, ARNs, account IDs |

## What every stack gets

| File | Purpose |
|---|---|
| `stack.yaml` | Stack name, adapter, environment boundary, and its forbidden literals for `check_principles.py` |
| `profiles.yml` | `local` (DuckDB) + `dev` (personal sandbox) + `ci` + `stg`/`prod` targets, all from environment variables |
| `requirements-stack.txt` | dbt core + the stack's adapter |
| `domains/sales/orchestration/` | The domain's schedule (Airflow DAG, or a Databricks job) |
| `libs/de_common/dbt_runner.py` | How Airflow runs dbt on this stack (Airflow stacks only) |
| `platform/terraform/main.tf` | Schemas per domain × layer and gold-only grants |
| `.github/workflows/stack-validate.yml` | PR check: `dbt parse` and `terraform validate` offline; `dbt build --empty` once connected |
| `.github/workflows/cd.yml` | merge → stg, release tag → prod (with approval): Terraform, dbt build, publish orchestration |
| `.github/instructions/orchestration.instructions.md` | Copilot rules for the stack's orchestration files |

Every stack is checked by `scripts/verify-all-stacks.sh`: architecture checks, an offline `dbt parse`
with the stack's own adapter, and a full local build. Each stack's Terraform passes
`terraform validate` with its provider.

## Native alternatives

dbt is the common transform layer, which is why the method, checks, and demo are identical on all five.
Each stack has native options (Dataform, Lakeflow Declarative Pipelines, Snowflake dynamic tables,
Fabric notebooks, Glue jobs). Adopt one through an ADR, and add the matching checks to
`tools/check_principles.py` in the same PR.
