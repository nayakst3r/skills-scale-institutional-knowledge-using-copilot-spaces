# This environment's Fabric workspace and warehouse. Schemas are created by dbt; gold read access is
# granted by macros/grants.sql (Fabric has no Terraform resource for schema grants).
terraform {
  backend "azurerm" {} # storage account/container/key passed at init: -backend-config=...
  required_providers {
    fabric = { source = "microsoft/fabric", version = ">= 1.0" }
  }
}

provider "fabric" {} # auth from the environment (azure/login OIDC: FABRIC_USE_OIDC, FABRIC_CLIENT_ID, FABRIC_TENANT_ID)

variable "env" { type = string }
variable "capacity_id" { type = string }
variable "engineers_group_id" {
  type        = string
  description = "Entra ID group of data engineers (Contributor in dev, Viewer in stg/prod)"
}

resource "fabric_workspace" "env" {
  display_name = "de-${var.env}"
  description  = "Data platform (${var.env}). Deployed by CI only."
  capacity_id  = var.capacity_id
}

resource "fabric_warehouse" "main" {
  display_name = "de_warehouse"
  workspace_id = fabric_workspace.env.id
}

resource "fabric_workspace_role_assignment" "engineers" {
  workspace_id = fabric_workspace.env.id
  principal = {
    id   = var.engineers_group_id
    type = "Group"
  }
  role = var.env == "dev" ? "Contributor" : "Viewer" # P9: people are read-only outside dev
}
