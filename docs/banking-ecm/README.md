# OctoAcme Financial Group — Banking ECM Business Specification & Reporting Requirements

**Document set ID:** OAFG-BSR-2026
**Version:** 1.0
**Status:** Baselined for build
**Data model baseline:** Databricks Lakehouse Industry Data Model — Banking, `v1_ecm` (Expanded Coverage Model)
**Physical baseline:** Unity Catalog catalog `banking_ecm` — 19 schemas, 501 tables, 19,792 attributes, 3,301 foreign keys, 90 metric views

---

## 1. What this document set is

This is the complete business specification and reporting requirements baseline for the **OctoAcme Financial Group (OAFG) Enterprise Risk, Finance & Customer Reporting Platform**, built on the Databricks Banking Expanded Coverage Model (ECM).

It is written to be **buildable without further clarification**. Every business rule names its source schema, table and columns. Every report names its grain, its measures, its filters, its latency budget, its entitlement class, and its acceptance test. Every metric has a single certified definition that no downstream consumer may redefine.

It is deliberately hard. OAFG runs dual-GAAP impairment (IFRS 9 and CECL), reports into four supervisory regimes, and must satisfy BCBS 239 principles on risk data aggregation. The specification does not simplify any of that away.

## 2. Reading order

| # | Document | Read it when you need to know |
|---|---|---|
| 00 | [Programme charter, scope and glossary](./00-programme-charter-and-scope.md) | Why the platform exists, what is in and out of scope, what every term means |
| 01 | [Personas and service model](./01-personas-and-service-model.md) | Who consumes the platform, what they decide, what they are entitled to see |
| 02 | [Business specifications](./02-business-specifications.md) | The 96 numbered business rules, with formulas and source columns |
| 03 | [Reporting requirements](./03-reporting-requirements.md) | The 40 report specifications, per persona |
| 04 | [Data contracts and freshness SLOs](./04-data-contracts-and-slos.md) | What each source system must deliver, by when, at what quality |
| 05 | [Semantic layer and certified metrics](./05-semantic-layer-and-metrics.md) | The 50 certified metric definitions and conformed dimensions |
| 06 | [Governance, security and controls](./06-governance-security-and-controls.md) | Entitlements, masking, lineage, retention, BCBS 239 evidence |
| 07 | [Acceptance criteria and test plan](./07-acceptance-criteria-and-test-plan.md) | How each requirement is proven done |
| 08 | [Non-functional requirements](./08-non-functional-requirements.md) | Scale, latency, concurrency, availability, recovery, cost |
| 09 | [Delivery roadmap and RACI](./09-delivery-roadmap-and-raci.md) | Phasing, milestones, decision rights, risks |

## 3. Identifier conventions

Every requirement in this set carries a stable identifier. Identifiers are never reused, never renumbered, and are cited verbatim in Jira, in test cases, and in regulatory evidence packs.

| Prefix | Meaning | Defined in |
|---|---|---|
| `P-nn` | Persona | 01 |
| `BR-XXX-nnn` | Business rule, where `XXX` is the domain code | 02 |
| `RPT-nnn` | Report specification | 03 |
| `DC-nnn` | Data contract | 04 |
| `MET-nnn` | Certified metric | 05 |
| `DIM-nnn` | Conformed dimension | 05 |
| `CTL-nnn` | Control | 06 |
| `ENT-n` | Entitlement class | 06 |
| `AC-nnn` | Acceptance criterion | 07 |
| `NFR-nnn` | Non-functional requirement | 08 |
| `RSK-nnn` | Programme risk | 09 |

Domain codes used in `BR-XXX-nnn`: `CRR` credit risk, `IMP` impairment, `CAP` capital, `LIQ` liquidity, `MKT` market and counterparty risk, `COL` collateral, `AML` financial crime, `FRD` fraud, `PAY` payments, `FIN` finance and ledger, `CUS` customer, `CHN` channel, `MDL` model risk, `AUD` audit, `ORX` operational risk, `DQ` data quality, `REG` regulatory reporting.

## 4. Precedence

Where documents conflict, precedence is:

1. Regulatory rule text as interpreted by Group Regulatory Policy (external to this set)
2. Document 02, business specifications
3. Document 05, certified metrics
4. Document 03, reporting requirements
5. Everything else

A report specification may never restate a metric formula. It cites the `MET-nnn` identifier. This is the single most important rule in the document set, and the one most often broken.

## 5. Change control

Changes to a `BR`, `MET` or `DC` identifier require the change-control path in [06](./06-governance-security-and-controls.md#7-change-control). Changes to a metric that is board-reported or regulatory-submitted additionally require sign-off from the Group Chief Risk Officer (P-01) and the Chief Data Officer (P-12), and trigger a mandatory restatement assessment under `BR-DQ-009`.

## 6. Using this set with Copilot Spaces

This set is written to be loaded as source material into a Copilot Space so that role-specific questions can be answered from a single institutional baseline. Recommended Space composition:

- **Risk & Capital Space** — documents 00, 01, 02, 05, 06 plus the `risk`, `loan`, `collateral`, `treasury` schema DDL
- **Financial Crime Space** — documents 00, 01, 02, 03, 06 plus the `compliance`, `fraud`, `customer`, `payment` schema DDL
- **Finance & Regulatory Reporting Space** — documents 00, 02, 03, 04, 07 plus the `ledger`, `treasury`, `reference` schema DDL
- **Data Platform Space** — documents 04, 05, 06, 08 plus the full `banking_ecm` DDL and the metric view definitions

Persona prompts for each Space are given at the end of [01](./01-personas-and-service-model.md#9-persona-prompts-for-copilot-spaces).
