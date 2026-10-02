# One Glue database per domain x layer, stored in this environment's lake bucket.
terraform {
  backend "s3" {} # bucket/key/region passed at init: -backend-config=...
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
}

provider "aws" {
  region = var.region
}

variable "region" { type = string }
variable "env" { type = string }
variable "lake_bucket" { type = string }
variable "domains" {
  type    = list(string)
  default = ["sales", "finance", "customer"]
}
variable "gold_reader_role_arn" {
  type        = string
  description = "IAM role (BI, ML, other domains) allowed to read every domain's gold"
}

locals {
  schemas = { for pair in setproduct(var.domains, ["bronze", "silver", "gold"]) :
  "${pair[0]}_${pair[1]}" => { domain = pair[0], layer = pair[1] } }
}

resource "aws_glue_catalog_database" "medallion" {
  for_each     = local.schemas
  name         = each.key
  location_uri = "s3://${var.lake_bucket}/${each.key}/"
  parameters   = { domain = each.value.domain, layer = each.value.layer, env = var.env }
}

# P3: other domains may read only gold (Lake Formation).
resource "aws_lakeformation_permissions" "gold_readers" {
  for_each    = { for k, v in local.schemas : k => v if v.layer == "gold" }
  principal   = var.gold_reader_role_arn
  permissions = ["SELECT", "DESCRIBE"]
  table {
    database_name = aws_glue_catalog_database.medallion[each.key].name
    wildcard      = true
  }
}
