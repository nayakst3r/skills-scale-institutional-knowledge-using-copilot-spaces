## This repo's stack: Google Cloud
- Warehouse: **BigQuery**. Each environment is its own GCP project; schemas (datasets) are `<domain>_<layer>`.
- dbt adapter: `dbt-bigquery`. Partitioning via `physical_layout()` becomes `partition_by` (date) + `cluster_by`.
- Orchestration: **Cloud Composer (Airflow 2)**. `dbt_build()` runs the dbt image as a **Cloud Run job**.
- Landing: GCS → bronze (BigQuery external or loaded tables). Streaming: Pub/Sub → Dataflow.
- Governance: Dataplex; PII `policy_tag` maps to a BigQuery policy tag (column-level security).
- CI/CD login: Workload Identity Federation (`google-github-actions/auth`). No JSON keys.
- Your sandbox: `gcloud auth application-default login`, then `DBT_TARGET=dev DBT_USER=<you> DE_GCP_PROJECT=de-dev dbt build --select tag:<domain>`.
