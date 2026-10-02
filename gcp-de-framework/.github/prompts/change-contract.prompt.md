---
name: change-contract
description: Safely change an existing table's schema (additive, or a versioned breaking change)
argument-hint: table=<domain>/<name> change=<what to change>
agent: agent
---
Change the schema of the table given in the chat message.

1. Read its contract and transform, and search the repo for every `ref(...)` to it (its consumers).
2. Classify the change as **additive** (new NULLABLE column) or **breaking** (remove, rename, type change,
   NULLABLE → REQUIRED). Tell me which, and why, before you edit.
3. Additive: add the column to the contract and transform, and bump MINOR.
4. Breaking: leave the existing table untouched. Create `<name>_v<N+1>` (contract + transform), mark the old
   contract `deprecated` with `replaced_by` and a `sunset_date` 60 days out, and list consumers that must migrate.
5. Run the "check: contract compatibility vs main" task and `make check`; fix every violation.
