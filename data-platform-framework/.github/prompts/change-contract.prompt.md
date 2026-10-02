---
name: change-contract
description: Safely change an existing table's schema (additive, or a versioned breaking change)
argument-hint: table=<domain>/<name> change=<what to change>
agent: agent
---
Change the schema of the table given in the chat message.

1. Read its contract and model, and search the repo for every `ref(...)` to it (its consumers).
2. Classify the change as **additive** (new NULLABLE column) or **breaking** (remove, rename, type change,
   NULLABLE → REQUIRED). Tell me which, and why, before you edit.
3. Additive: add the column to the contract, the model, and the sample CSV if it is a bronze column; bump MINOR.
4. Breaking: leave the existing table untouched. Create `<name>_v<N+1>` (contract + model `<domain>_<layer>_<name>_v<N+1>.sql` + tests), mark the old
   contract `deprecated` with `replaced_by` and a `sunset_date` 60 days out, and list consumers that must migrate.
5. Run the "check: contract compatibility vs main" task, `make check`, and `make local-build`; fix every failure.
