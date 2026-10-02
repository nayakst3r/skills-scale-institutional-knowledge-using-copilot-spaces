---
name: Terraform
description: Rules for platform infrastructure
applyTo: "platform/**/*.tf"
---
- Infrastructure lives only here; nothing is created by hand in the console in stg or prod.
- Never commit state, `*.tfvars` holding secrets, or service-account keys.
- Grant IAM to groups, not individual users. Grant cross-domain read access only on `*_gold` datasets.
- Changes here go in a platform-only PR (no domain feature code in the same PR).
