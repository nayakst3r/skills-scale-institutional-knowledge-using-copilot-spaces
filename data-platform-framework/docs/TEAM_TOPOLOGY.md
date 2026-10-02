# Team topology: 10 engineers

| Pod | People | Owns | GitHub team |
|---|---|---|---|
| Platform | 2 | `platform/`, `libs/`, `tools/`, `.github/`, `macros/`, `stacks/`, CI/CD, orchestrator, IAM | `@org/de-platform` |
| Sales domain | 3 | `domains/sales/` | `@org/de-sales` |
| Finance domain | 3 | `domains/finance/` | `@org/de-finance` |
| Customer domain | 2 | `domains/customer/` | `@org/de-customer` |

## Roles that rotate (so context doesn't sit with one person)
- **Architecture Guild**: 1 rep per pod plus the tech lead. Meets weekly for 30 minutes to review open ADRs and any PR labelled `needs-architecture`. Owns `ARCHITECTURE.md` and `AGENTS.md`.
- **Release captain** (weekly rotation): approves prod promotions and watches stg assertions.
- **Context curator** (monthly rotation): turns repeated review comments and AI mistakes into `AGENTS.md` rules or new checks in `tools/check_principles.py`.

## Rituals
| When | What | Output |
|---|---|---|
| Daily, 15 min | Stand-up, including "which contracts am I changing?" | Early conflict detection |
| Weekly, 30 min | Architecture Guild | Merged/declined ADRs |
| Bi-weekly | Retro: which bugs or reviews could a check have caught? | New fitness functions |
| Per new joiner | Pair on one PR end-to-end using `domains/sales/` as the template | Onboarded in a day |
