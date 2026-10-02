# Unity Catalog schemas per domain x layer in this environment's catalog, and gold-only read grants.
terraform {
  backend "s3" {} # or "azurerm" / "gcs": use the state store of the cloud your workspace runs on
  required_providers {
    databricks = { source = "databricks/databricks", version = ">= 1.50" }
  }
}

provider "databricks" {} # auth from the environment (DATABRICKS_HOST, DATABRICKS_AUTH_TYPE=github-oidc, ...)

variable "catalog" { type = string }
variable "domains" {
  type    = list(string)
  default = ["sales", "finance", "customer"]
}
variable "gold_readers_group" {
  type        = string
  description = "Account group allowed to read every domain's gold"
}

locals {
  schemas = { for pair in setproduct(var.domains, ["bronze", "silver", "gold"]) :
  "${pair[0]}_${pair[1]}" => { domain = pair[0], layer = pair[1] } }
}

resource "databricks_schema" "medallion" {
  for_each     = local.schemas
  catalog_name = var.catalog
  name         = each.key
  comment      = "${each.value.layer} layer of the ${each.value.domain} domain. Managed by Terraform."
  properties   = { domain = each.value.domain, layer = each.value.layer }
}

# P3: other domains may read only gold.
resource "databricks_grants" "gold_readers" {
  for_each = { for k, v in local.schemas : k => v if v.layer == "gold" }
  schema   = databricks_schema.medallion[each.key].id
  grant {
    principal  = var.gold_readers_group
    privileges = ["USE_SCHEMA", "SELECT"]
  }
}
