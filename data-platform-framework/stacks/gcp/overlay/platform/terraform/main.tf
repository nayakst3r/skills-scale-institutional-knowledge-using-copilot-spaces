# One schema (BigQuery dataset) per domain x layer, in this environment's project.
terraform {
  backend "gcs" {} # bucket passed at init: -backend-config="bucket=..."
  required_providers {
    google = { source = "hashicorp/google", version = ">= 6.0" }
  }
}

provider "google" {
  project = var.project_id
}

variable "project_id" { type = string }
variable "env" { type = string }
variable "location" {
  type    = string
  default = "EU"
}
variable "domains" {
  type    = list(string)
  default = ["sales", "finance", "customer"]
}
variable "gold_readers_group" {
  type        = string
  description = "Google group allowed to read every domain's gold, e.g. de-gold-readers@example.com"
}

locals {
  schemas = { for pair in setproduct(var.domains, ["bronze", "silver", "gold"]) :
  "${pair[0]}_${pair[1]}" => { domain = pair[0], layer = pair[1] } }
}

resource "google_bigquery_dataset" "medallion" {
  for_each   = local.schemas
  dataset_id = each.key
  location   = var.location
  labels     = { domain = each.value.domain, layer = each.value.layer, env = var.env }
}

# P3: other domains may read only gold.
resource "google_bigquery_dataset_iam_member" "gold_readers" {
  for_each   = { for k, v in local.schemas : k => v if v.layer == "gold" }
  dataset_id = google_bigquery_dataset.medallion[each.key].dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "group:${var.gold_readers_group}"
}
