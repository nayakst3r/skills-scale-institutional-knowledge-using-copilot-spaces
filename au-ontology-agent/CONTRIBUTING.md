# Contributing

The ontology is a product, not a project. Changes are routed by risk, not by
who is asking.

## Before you open a PR

    make gate          # ontology gate + structural contract + viewer check

All of it must pass. The gate is a required check on `main`.

## Change classes

Every change falls into one of four classes. `agent/change_policy.py` is the
implementation; this is the summary.

| Class | Examples | Route | Approver |
|---|---|---|---|
| Editorial | label, note, typo | auto-merge | none, logged |
| Additive | new class or attribute from a tier 1 source | auto-merge | none, logged |
| Additive | new class or attribute from tier 2–4 | human review | Domain Steward |
| Semantic | domain or range change, re-parenting, validity interval | human review | Domain Steward + Semantic Architect |
| Breaking | retire, merge, split, URI change | review board | Product Owner + 2LoD |

**Override:** anything touching an obligation, licence, prudential reference or
validity interval is never auto-merged, whatever its tier.

## Rules that are not negotiable

1. **Every assertion carries provenance.** A source URL and a retrieval date, or
   it does not go in.
2. **Agents do not grade their own work.** An agent may write `proposed`. Only a
   human moves an assertion to `validated`. The audit log detects violations.
3. **Confidence is explicit.** `curated`, `patterned`, `notVerified` — never
   implied by omission.
4. **The scenario suite is the contract.** A change that breaks a traversal fails
   the build. Fix the model or fix the scenario; do not delete the scenario.
5. **Structural findings are resolved, not suppressed.** Bidirectional edges and
   cycles are demoted to soft references with a stated reason. Deleting a
   relationship to make a gate pass is lying about the domain.

## Regenerating

    make model         # rebuild ECM + MVM from the ontology
    make artefacts     # DDL, DBML, metric SQL, tag taxonomy
    make viewer        # refresh the embedded viewer payload

`model/` and `viewer/` are committed on purpose. The diff is how model change is
reviewed. CI fails if they are stale.

## Attribute work

74 of 366 products are curated; 292 are pattern-generated and carry confidence
`notVerified`. Replacing a patterned product with sourced detail is the most
valuable contribution available. Prompts 19–23 in `prompts/domains.md` scope it.

State your source for every attribute. "It seems right" is not a source.
