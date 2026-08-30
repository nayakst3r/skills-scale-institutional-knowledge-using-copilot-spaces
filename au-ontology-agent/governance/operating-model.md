# Operating model — Australian banking ontology

## Decision rights (RACI)

| Activity | Ontology Product Owner | Semantic Architect | Domain Steward | Platform Eng | Risk (2LoD) | Internal Audit (3LoD) |
|---|---|---|---|---|---|---|
| Ontology strategy and roadmap | **A** | C | C | I | C | I |
| Accept auto-merged tier 1 change | **A** | I | I | R | I | I |
| Approve human-review change | A | C | **R** | I | C | I |
| Approve breaking change | **A** | R | C | I | **C** | I |
| Agent behaviour and prompts | A | C | I | **R** | C | I |
| Source tier assignment | A | **R** | C | I | C | I |
| Change-class policy | **A** | R | C | I | **C** | I |
| Kill-switch invocation | A | I | I | **R** | A | I |
| Independent assurance | I | I | I | I | C | **R** |

The Ontology Product Owner is the **FAR accountable person** for this capability
and holds the accountability statement. Not a committee.

## Roles

- **Ontology Product Owner** — accountable end to end. Owns the roadmap, the
  change-class policy, and the regulatory mapping. Single named individual.
- **Semantic Architect** — owns naming conventions, URI and namespace governance,
  modularisation, compatibility and deprecation rules.
- **Domain Stewards (federated)** — own concept proposals and business meaning in
  their domain: retail lending, deposits, cards, markets, insurance, payments,
  regulatory reporting. They approve human-review changes in their domain.
- **Platform Engineering** — runs the agents, the MCP servers, the audit log and
  the kill-switch. Cannot approve semantic change.
- **Risk and Compliance (2LoD)** — sets policy, challenges the auto-merge boundary,
  reviews the obligation mapping.
- **Internal Audit (3LoD)** — independent assurance over the control design and
  the audit evidence.

## Change classes and routing

| Class | Examples | Route | Approver |
|---|---|---|---|
| Editorial | label, note, typo | auto-merge | none (logged) |
| Additive | new class or property, tier 1 source | auto-merge | none (logged) |
| Additive | new class, tier 2–4 source | human review | Domain Steward |
| Semantic | domain/range change, re-parenting, validity interval | human review | Domain Steward + Semantic Architect |
| Breaking | retire, merge, split, URI change | review board | Product Owner + 2LoD |

**Override:** anything touching an obligation, licence, prudential reference or
validity interval is never auto-merged, regardless of tier.

## Cadence and SLA

| Activity | Cadence | SLA |
|---|---|---|
| Tier 1 source poll (CDR, legislation) | daily | — |
| Tier 2–3 poll (standards, bank disclosure) | weekly | — |
| Human-review queue triage | daily | 2 business days to decision |
| Review board | fortnightly | 10 business days for breaking change |
| Drift re-verification sample | monthly | 5% of verified assertions |
| Model and agent review | quarterly | — |
| Independent assurance | annual | — |

## Controls to obligations

| Control | Satisfies |
|---|---|
| Named accountable person + accountability statement | FAR |
| Board-approved tolerance levels for the ontology capability | CPS 230 |
| Material service provider register entry for the platform vendor | CPS 230 |
| Incident notification: 72h material, 24h critical-operation breach | CPS 230 paras 33, 42 |
| Information asset classification for ontology store and MCP servers | CPS 234 |
| Data lineage, quality metrics, metadata repository, business glossary | CPG 235 |
| Three lines of defence with segregation of duties | CPS 220 |
| Immutable hash-chained audit log | CPS 230, CPG 235, audit evidence |
| Human-in-the-loop for semantic and breaking change | Voluntary AI Safety Standard Guardrail 5 |
| AI management system, risk register, agent inventory | ISO/IEC 42001, NIST AI RMF |
| Confidence labelling; no self-promotion to verified | ASIC REP 798 expectations, s912A |
| Kill-switch and rollback | CPS 230 operational resilience |

## Failure modes to design against

Documented causes of enterprise ontology failure, and the control that answers each:

- **Treated as a project, not a product** → product owner, standing budget, roadmap.
- **Model too large to start** → scenario suite defines minimum viable coverage.
- **Ownership and decision rights unclear** → the RACI above, with one accountable name.
- **Drifts silently from reality** → monthly re-verification sample, drift alerts.
- **Agent output trusted as fact** → confidence field, no self-promotion, provenance required.
- **No feedback loop from consumers** → domain stewards sit in the consuming domains.
