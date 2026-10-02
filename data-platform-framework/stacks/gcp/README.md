# Stack: Google Cloud

| Concern | Choice |
|---|---|
| Warehouse | BigQuery; one GCP project per environment |
| Transform | dbt (`dbt-bigquery`) |
| Orchestration | Cloud Composer (Airflow 2); dbt runs as a Cloud Run job |
| Infra | Terraform (`hashicorp/google`) |
| CI/CD login | Workload Identity Federation (`google-github-actions/auth`) |
| PII | `policy_tag` → BigQuery policy tags (Dataplex) |
| Native alternative | Dataform instead of dbt (needs an ADR and matching checks) |

## Connect GitHub to GCP
1. Create a Workload Identity Pool + provider for GitHub, and a deploy service account per environment.
2. Repo/environment variables: `GCP_WIF_PROVIDER`, `GCP_DEPLOY_SA`, `DE_GCP_PROJECT` (per environment),
   `DE_GCP_REGION`, `DE_TF_STATE_BUCKET`, `DE_GOLD_READERS`, `DE_COMPOSER_BUCKET`, `DE_DBT_IMAGE`.
3. Terraform state goes to the GCS bucket in `DE_TF_STATE_BUCKET` (one per environment).
Until the variables exist, the cloud steps are skipped and the offline checks still run.
