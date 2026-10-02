---
name: Data contracts
description: Rules for editing data contracts (the public API of a table)
applyTo: "domains/**/contracts/*.yaml"
---
- A contract matches `tools/contract.schema.json`; the file name equals `name`.
- Additive change (new NULLABLE column): bump MINOR (`1.1.0` → `1.2.0`).
- Never remove or rename a column, change its type, or make it REQUIRED in place. That's breaking:
  create `<name>_v<N+1>.yaml` (version `N+1.0.0`) and a new transform, keep the old one,
  and set `deprecated: { replaced_by, sunset_date }` on the old contract.
- Columns with personal data need `pii: true` and a `policy_tag`.
- Changing a contract needs the platform team's review (CODEOWNERS). Say so in the PR.
