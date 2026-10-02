# One schema per domain x layer in this environment's database, and gold-only read grants.
terraform {
  backend "s3" {} # or "azurerm" / "gcs": use your organization's state store
  required_providers {
    snowflake = { source = "snowflakedb/snowflake", version = ">= 1.0" }
  }
}

provider "snowflake" {} # auth from the environment (SNOWFLAKE_ORGANIZATION_NAME, SNOWFLAKE_ACCOUNT_NAME, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY, ...)

variable "database" {
  type        = string
  description = "This environment's database, e.g. DE_STG"
}
variable "domains" {
  type    = list(string)
  default = ["sales", "finance", "customer"]
}
variable "gold_reader_role" {
  type        = string
  description = "Account role allowed to read every domain's gold, e.g. DE_GOLD_READER"
}

locals {
  schemas = { for pair in setproduct(var.domains, ["bronze", "silver", "gold"]) :
  upper("${pair[0]}_${pair[1]}") => { domain = pair[0], layer = pair[1] } }
}

resource "snowflake_database" "env" {
  name    = var.database
  comment = "Data platform. Deployed by CI only."
}

resource "snowflake_schema" "medallion" {
  for_each = local.schemas
  database = snowflake_database.env.name
  name     = each.key
  comment  = "${each.value.layer} layer of the ${each.value.domain} domain. Managed by Terraform."
}

# P3: other domains may read only gold (schema usage + all current and future tables).
resource "snowflake_grant_privileges_to_account_role" "gold_usage" {
  for_each          = { for k, v in local.schemas : k => v if v.layer == "gold" }
  account_role_name = var.gold_reader_role
  privileges        = ["USAGE"]
  on_schema {
    schema_name = snowflake_schema.medallion[each.key].fully_qualified_name
  }
}

resource "snowflake_grant_privileges_to_account_role" "gold_future_tables" {
  for_each          = { for k, v in local.schemas : k => v if v.layer == "gold" }
  account_role_name = var.gold_reader_role
  privileges        = ["SELECT"]
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = snowflake_schema.medallion[each.key].fully_qualified_name
    }
  }
}
