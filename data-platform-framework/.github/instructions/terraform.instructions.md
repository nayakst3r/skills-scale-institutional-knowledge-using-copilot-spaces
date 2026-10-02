---
name: Terraform
description: Rules for platform infrastructure
applyTo: "platform/**/*.tf"
---
- Infrastructure lives only here; nothing is created by hand in the console in stg or prod.
- Never commit state, `*.tfvars` holding secrets, or credentials of any kind.
- Grant access to groups or roles, not individual users. Grant cross-domain read access only on `*_gold` schemas.
- Changes here go in a platform-only PR (no domain feature code in the same PR).
