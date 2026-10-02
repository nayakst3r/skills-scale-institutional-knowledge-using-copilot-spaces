# Datasets are created from a list, so adding a domain is one line, reviewed by platform.
locals {
  domains = ["sales", "finance", "customer"]
  layers  = ["bronze", "silver", "gold"]
  datasets = { for pair in setproduct(local.domains, local.layers) :
  "${pair[0]}_${pair[1]}" => { domain = pair[0], layer = pair[1] } }
}

resource "google_bigquery_dataset" "medallion" {
  for_each   = local.datasets
  project    = var.project_id
  dataset_id = each.key
  location   = var.location
  labels     = { domain = each.value.domain, layer = each.value.layer, env = var.env }
}

# P3: other domains may read only gold.
resource "google_bigquery_dataset_iam_member" "cross_domain_gold_reader" {
  for_each   = { for k, v in local.datasets : k => v if v.layer == "gold" }
  project    = var.project_id
  dataset_id = google_bigquery_dataset.medallion[each.key].dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "group:de-all-readers@example.com"
}

variable "project_id" { type = string }
variable "location" {
  type    = string
  default = "EU"
}
variable "env" { type = string }
