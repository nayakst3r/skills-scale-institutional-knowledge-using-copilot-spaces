# 09 — Delivery Roadmap, RACI and Risks

**Document ID:** OAFG-BSR-2026-09 · **Version:** 1.0 · **Owner:** Programme Director · **Approver:** Group Executive Committee

---

## 1. Sequencing principle

The roadmap is sequenced by **dependency and regulatory exposure**, not by persona seniority or by ease. Two consequences follow, and both have been challenged and upheld.

1. **Data quality and entitlement come first.** A report built before its controls is a report that has to be rebuilt. The first release delivers no business report at all.
2. **The hardest latency requirement comes early.** `RPT-012` and its 09:00 deadline is delivered in phase 2, not last, because everything about the platform's operational design is shaped by it. Discovering in phase 5 that the architecture cannot meet it would be fatal.

## 2. Phases

### Phase 0 — Foundation (months 1–3)

| Deliverable | Acceptance |
|---|---|
| `banking_ecm` Silver layer instantiated in Unity Catalog, all 19 schemas | `AC-152`, `AC-153` pass at scale |
| Contracts `DC-001`, `DC-004`, `DC-007`, `DC-014`, `DC-021` live with test suites | L1 criteria pass for those five |
| Entitlement classes `ENT-1` to `ENT-7` implemented and tested | `AC-088`, `AC-122` pass from every class |
| Data quality framework and `RPT-038` | `AC-271` passes |
| CDE register with named stewards | `AC-151` passes, zero unowned CDEs |
| Lineage generation from deployed code | `AC-272` partial, lineage only |

**Exit gate.** No business report is delivered in this phase. The gate is that `RPT-038` is live, every phase-0 contract is under test, and `AC-088` passes in full. P-14 records non-objection.

### Phase 1 — Credit and impairment (months 4–8)

| Deliverable | Reports | Key rules |
|---|---|---|
| Credit exposure and concentration | RPT-003, RPT-018, RPT-019 | `BR-CRR-001` to `BR-CRR-006`, `BR-CRR-011`, `BR-MKT-003`, `BR-COL-001` to `BR-COL-003` |
| Impairment | RPT-004, RPT-005 | `BR-IMP-001` to `BR-IMP-012` |
| Watchlist and covenants | RPT-006, RPT-007 | `BR-CRR-009`, `BR-CRR-013` |
| Contracts `DC-006`, `DC-008`, `DC-022` | | |

**Exit gate.** `RPT-004` publishes with a zero attribution residual and a clean risk-to-finance reconciliation for two consecutive month ends. This is objective O2.

### Phase 2 — Liquidity, capital and treasury (months 7–11)

| Deliverable | Reports | Key rules |
|---|---|---|
| Daily liquidity | RPT-012 | `BR-LIQ-001` to `BR-LIQ-004` |
| NSFR, ALCO, FTP | RPT-013, RPT-014, RPT-015 | `BR-LIQ-002`, `BR-LIQ-005`, `BR-LIQ-006` |
| Capital and stress | RPT-009 partial, RPT-016 | `BR-CAP-001` to `BR-CAP-008` |
| Nostro | RPT-027 | `BR-LIQ-007` |
| Contracts `DC-012`, `DC-013`, `DC-015` | | |

**Exit gate.** `RPT-012` delivers before 09:00 for 20 consecutive business days, including at least one day on which a contract was late and the qualified-publication path was exercised. This is `NFR-004` and it is proven in production, not in test.

### Phase 3 — Financial crime and fraud (months 9–13)

| Deliverable | Reports | Key rules |
|---|---|---|
| Filing deadlines and KYC | RPT-021, RPT-022 | `BR-AML-001` to `BR-AML-003`, `BR-AML-007` |
| Alert and case operations | RPT-020 | `BR-AML-005`, `BR-AML-006` |
| Screening and coverage | RPT-023 | `BR-AML-004`, `BR-AML-009`, `BR-AML-010` |
| Fraud | RPT-024, RPT-025 | `BR-FRD-001` to `BR-FRD-004` |
| Contracts `DC-018`, `DC-019`, `DC-020` | | |

**Exit gate.** `AC-088` re-tested in full against every phase-3 report and export. Median escalated case handling time measured, with the baseline established for objective O4. `RPT-020` context panel meets `NFR-006` at production scale.

### Phase 4 — Finance, regulatory and channels (months 12–17)

| Deliverable | Reports | Key rules |
|---|---|---|
| Close and reconciliation | RPT-028, RPT-029, RPT-030 | `BR-FIN-001` to `BR-FIN-006` |
| Regulatory submission | RPT-009 full, RPT-010, RPT-011 | `BR-REG-001` to `BR-REG-008` |
| Payments and channels | RPT-026, RPT-032, RPT-033 | `BR-PAY-001` to `BR-PAY-003`, `BR-CHN-001` to `BR-CHN-003` |
| Contracts `DC-002`, `DC-003`, `DC-005`, `DC-016`, `DC-017` | | |

**Exit gate.** One full quarterly submission cycle produced from the platform in parallel with the legacy process, reconciling exactly, with `AC-174` reproducibility proven on the frozen snapshot. Close completed in 8 working days, on the path to objective O6.

### Phase 5 — Governance, front line and completion (months 16–21)

| Deliverable | Reports | Key rules |
|---|---|---|
| Model risk | RPT-034, RPT-035 | `BR-MDL-001` to `BR-MDL-005` |
| Audit and operational risk | RPT-036, RPT-037 | `BR-AUD-001`, `BR-AUD-002`, `BR-ORX-001`, `BR-ORX-002` |
| Board and appetite | RPT-001, RPT-002 | `BR-CRR-012` |
| Front line and wealth | RPT-008, RPT-031, RPT-040 | `BR-CUS-001` to `BR-CUS-003` |
| Full attestation | RPT-039 | BCBS 239 evidence complete |
| Contracts `DC-009` to `DC-011`, `DC-023` to `DC-026` | | |

**Exit gate.** All six programme objectives measured and met on `RPT-039`. Legacy marts decommissioned. P-14 issues a closing opinion.

## 3. What is deliberately last

| Deferred to phase 5 | Why |
|---|---|
| RPT-001 Board Risk Dashboard | It aggregates everything else. Building it first would mean building it five times |
| RPT-031 Client Relationship View | Its entitlement is the most complex in the estate and depends on every other domain being correct first |
| Legacy decommissioning | Nothing is switched off until its replacement has run in parallel for a full reporting cycle |

## 4. RACI

**R** responsible · **A** accountable · **C** consulted · **I** informed

| Activity | Programme Director | P-01 | P-04 | P-05 | P-06 | P-07 | P-12 | P-13 | P-14 | Platform Eng |
|---|---|---|---|---|---|---|---|---|---|---|
| Programme scope and phasing | A | C | C | C | C | C | R | I | I | C |
| Business rule definition | I | A for risk | A for treasury | C | A for finance | A for crime | R | C | I | C |
| Certified metric definition | I | C | C | C | C | C | A | C | I | R |
| Data contract agreement | I | I | C | C | C | C | A | I | I | R |
| Entitlement model | I | C | I | I | I | A for `ENT-3` | A | I | C | R |
| `CTL-011` design and testing | I | I | I | I | I | A | R | I | C | R |
| Report specification | I | C | C | C | C | C | C | C | I | R |
| Report acceptance | I | A for their own | A for their own | A for their own | A for their own | A for their own | C | A for their own | I | R |
| Data quality remediation | I | C | C | C | C | C | A | I | C | R |
| Restatement decisions | I | C | C | A | A | C | R | C | C | I |
| Submission sign-off | I | C | C | A | C | I | C | I | C | I |
| Model approval for use | I | C | I | I | I | I | C | A | C | I |
| Control operation | I | A for risk controls | A for treasury | A for submission | A for finance | A for crime | A for data | A for model | C | R |
| Independent assurance | I | I | I | I | I | I | I | I | A | I |
| Legacy decommissioning | A | C | C | C | C | C | R | I | C | R |

Two rules govern this matrix. Exactly one **A** per activity per domain, and the Chief Audit Executive is never **A** or **R** for anything the third line will later test.

## 5. Programme risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| `RSK-001` | Source systems cannot meet the `DC-012` 04:30 window, making `NFR-004` unachievable | Medium | Critical | Window agreed and tested in phase 0, before any dependent design. If it cannot be met, the platform architecture changes, not the deadline | P-04 |
| `RSK-002` | Origination PD is not retained historically, so `BR-IMP-002` quantitative SICR cannot be tested for the back book | High | High | Quantified in phase 1 discovery. Affected population reported explicitly on `RPT-005` rather than being defaulted to stage 1. Remediation is a separate data recovery project | P-02 |
| `RSK-003` | A `CTL-011` disclosure occurs during development or testing | Low | Critical | SAR data never leaves production. Pre-production extracts exclude it entirely. `AC-088` runs on every build | P-07 |
| `RSK-004` | Business units rebuild metrics in their own tools, defeating `SEM-01` | High | High | `BR-DQ-007` detection scan weekly, and `NFR-073` ten-day delivery so that the certified path is faster than the workaround. The second matters more than the first | P-12 |
| `RSK-005` | Connected client group derivation disagrees with the credit function's manual view | Medium | High | Parallel run in phase 1 with every difference investigated and either fixed or documented as a definitional change | P-02 |
| `RSK-006` | Regulatory change during delivery invalidates a rule | High | Medium | Rules are versioned and dated. Regulatory Policy owns interpretation, per `ASM-03`. Change is absorbed through change control, not through rework | P-05 |
| `RSK-007` | Data quality in the back book is worse than assumed, blocking phase gates | High | High | Quality measured in phase 0 before any commitment to phase dates. Gates permit qualified publication with disclosed gaps, per `BR-DQ-012`, rather than blocking indefinitely | P-12 |
| `RSK-008` | Model dependency metadata is incomplete, so `BR-MDL-005` cannot answer the supervisory question | Medium | High | Dependency recorded at certification, enforced as a certification precondition rather than collected later | P-13 |
| `RSK-009` | Entitlement complexity for `ENT-4` makes `RPT-031` unbuildable within phase 5 | Medium | Medium | `ENT-4` scoping proven in phase 0 against a synthetic portfolio before any front-line report is scheduled | P-12 |
| `RSK-010` | Legacy marts are not decommissioned, so two versions of the truth persist indefinitely | High | High | Decommissioning is a phase-5 exit gate with executive accountability, not a follow-on activity. A parallel-running legacy mart past its agreed date is escalated to the Executive Committee monthly | Programme Director |
| `RSK-011` | Close acceleration to six days is resisted because task owners are outside the programme's control | Medium | Medium | `RPT-028` makes lateness visible by owner from phase 4, which changes the conversation from opinion to evidence | P-06 |
| `RSK-012` | The four-hour ad-hoc objective is met for anticipated questions only | Medium | High | Capability gaps logged when a request cannot be served from the certified layer. The gap log, not the success rate, drives the semantic layer roadmap | P-05 |

## 6. Programme-level acceptance

The programme is complete when, and only when, all six objectives from [00, section 2.1](./00-programme-charter-and-scope.md#21-programme-objectives) are measured and met on `RPT-039` for two consecutive quarters, every legacy mart in scope is decommissioned, and P-14 has issued a closing opinion with no unremediated finding rated high or above.

Partial completion is not completion. A platform that meets five objectives and leaves the sixth has left the institution with the same problem it started with, in a more expensive form.
