# 06 — Governance, Security and Controls

**Document ID:** OAFG-BSR-2026-06 · **Version:** 1.0 · **Owner:** Chief Data Officer (P-12) · **Non-objection:** Chief Audit Executive (P-14)

---

## 1. Entitlement classes

Entitlement is assigned to a persona, enforced in Unity Catalog, and never duplicated in a reporting tool, per `ASM-05`. A report tool that implements its own row-level security is a control failure under `CTL-003`, because it creates a second place for the rule to be wrong.

| ID | Class | Assigned to | Row scope | Column scope |
|---|---|---|---|---|
| `ENT-1` | Executive aggregate | P-01, Board | All entities, aggregate grain only | No party identifiers. Counterparty legal name only where `MET-017` identifies a large exposure |
| `ENT-2` | Risk analyst | P-02, P-03, P-13, Operational Risk | All entities, all exposure grain | Counterparty legal name and internal identifiers. All party PII masked |
| `ENT-3` | Financial crime | P-07, P-08, P-09 | All entities, all grain | Full party PII. **The only class with SAR visibility** |
| `ENT-4` | Front line | P-10, P-11, business heads | Restricted to assigned portfolio or business unit | Client PII for assigned clients. **No AML or SAR data of any kind** |
| `ENT-5` | Finance and treasury | P-04, P-05, P-06 | All entities, financial grain | Counterparty names. Party PII only where a regulatory return requires it |
| `ENT-6` | Audit | P-14 and audit staff | All entities, all grain, including Silver layer | Full access under audit mandate, every access logged and reported to P-12 |
| `ENT-7` | Data governance | P-12 and stewards | Metadata, lineage, quality results, access logs | No business data values beyond what profiling requires. Never unmasked PII |

### 1.1 Class assignment rules

- A person holds exactly one class. Multiple classes create an unresolvable question about which applies, and the answer in practice is always "the most permissive", which is not the intended answer.
- A person moving role has their class changed, never added to.
- Elevated access for a specific investigation is granted as a time-boxed grant with an expiry, an approver and a recorded purpose. It expires automatically. There is no permanent elevation.
- Service principals hold their own class, never a person's.

### 1.2 Row-level security

| Scope rule | Applies to | Source of the restriction |
|---|---|---|
| Legal entity | `ENT-5` where an entity restriction applies | `ledger.legal_entity` |
| Assigned client portfolio | `ENT-4` | `channel.rm_client_assignment`, `customer.customer_relationship_manager` |
| Assigned account portfolio | `ENT-4` | `account.rm_account_assignment` |
| Assigned wealth portfolio | `ENT-4` | `wealth.portfolio_assignment` |
| Assigned investigation queue | `ENT-3` investigators | Case assignment in `compliance.aml_case`, `fraud.case` |
| Line of business | `ENT-4` business heads | `ledger.profit_center` hierarchy |

Assignment changes propagate within 15 minutes. A termination event from `DC-025` revokes access immediately, not at the next refresh. This asymmetry is deliberate: granting late is an inconvenience, revoking late is an incident.

### 1.3 Column masking

| Column class | Columns | `ENT-1` | `ENT-2` | `ENT-3` | `ENT-4` | `ENT-5` | `ENT-6` | `ENT-7` |
|---|---|---|---|---|---|---|---|---|
| Government identifiers | `national_id_number`, `tax_identification_number`, `passport_number` | Hidden | Masked | Clear | Masked | Conditional | Clear | Hidden |
| Contact | `primary_email_address`, `primary_phone_number` | Hidden | Masked | Clear | Clear for assigned | Masked | Clear | Hidden |
| Personal | `date_of_birth`, `primary_address_line_1`, `primary_address_line_2` | Hidden | Masked | Clear | Clear for assigned | Masked | Clear | Hidden |
| Account identifiers | `account_number`, `card_number_last_four` | Hidden | Masked | Clear | Clear for assigned | Clear | Clear | Hidden |
| Technical | `ip_address`, `device_fingerprint`, `geolocation_latitude`, `geolocation_longitude` | Hidden | Hidden | Clear | Hidden | Hidden | Clear | Hidden |
| SAR indicators | `sar_filed_flag`, `sar_filing_date`, all of `fraud.sar_filing` | **Hidden** | **Hidden** | Clear | **Hidden** | **Hidden** | Clear | **Hidden** |

"Masked" means a deterministic, non-reversible transformation that preserves join capability without revealing the value. "Hidden" means the column does not appear in the result at all. Hidden is stronger and is used wherever the existence of a value is itself information.

`ENT-5` conditional access to government identifiers is granted per regulatory return, scoped to the population of that return, time-boxed to the submission window.

---

## 2. Control register

| ID | Control | Type | Frequency | Owner | Evidence |
|---|---|---|---|---|---|
| `CTL-001` | Exposure population and measure integrity | Detective | Daily | P-02 | `BR-CRR-001`, `BR-CRR-002` rule results on `RPT-038` |
| `CTL-002` | Connected group, large exposure and concentration | Detective | Daily | P-02 | `RPT-003` with the stored-versus-calculated flag comparison |
| `CTL-003` | Entitlement enforcement at a single layer | Preventive | Continuous | P-12 | Unity Catalog policy inventory; detection scan for tool-level security |
| `CTL-004` | Origination and conversion factor governance | Detective | Monthly | P-02 | `RPT-008`, `BR-CRR-006` verification results |
| `CTL-005` | Rating currency and override validity | Detective | Monthly | P-03, P-13 | `RPT-005`, `RPT-035` |
| `CTL-006` | Watchlist trigger completeness | Detective | Daily | P-02 | `RPT-006` trigger-by-trigger reconciliation to source conditions |
| `CTL-007` | Non-performing classification and contagion | Detective | Monthly | P-02 | `RPT-004`, contagion quantification |
| `CTL-008` | Limit utilisation and hard-stop enforcement | Preventive and detective | Daily | P-01 | `RPT-003`, origination block log |
| `CTL-009` | Risk appetite threshold governance | Detective | Monthly | P-01 | `RPT-002` governance-exception panel |
| `CTL-010` | Covenant testing completeness | Detective | Daily | P-03 | `RPT-007`, reporting-breach section |
| `CTL-011` | **SAR confidentiality and inference prevention** | Preventive | Continuous | P-07 | Masking policy inventory, inference assessment records, access log review |
| `CTL-012` | Impairment governance | Detective | Monthly | P-02, P-06 | `RPT-004` with zero residual, overlay register, override register |
| `CTL-013` | Collateral valuation currency and eligibility | Detective | Daily | P-02 | `RPT-019` stale-valuation and wrong-way-collateral sections |
| `CTL-014` | Privacy, consent and data subject rights | Preventive | Continuous | P-12 | Consent propagation log, request register with deadline position |
| `CTL-015` | Risk to finance provision reconciliation | Detective | Monthly | P-06 | `RPT-004` section 7, `RPT-029` |
| `CTL-016` | Capital computation and buffer monitoring | Detective | Quarterly | P-04 | `RPT-009` recomputation results |
| `CTL-017` | Stress run completeness and immutability | Preventive | Per run | P-01 | `RPT-016` run inventory, suppression evidence |
| `CTL-018` | Model inventory, validation and approved use | Preventive and detective | Monthly | P-13 | `RPT-034`, fallback quantification |
| `CTL-019` | Cost and capital allocation integrity | Detective | Monthly | P-06 | `RPT-030` allocation reconciliation |
| `CTL-020` | Liquidity computation and constraint identification | Detective | Daily | P-04 | `RPT-012`, binding-constraint evidence |
| `CTL-021` | FTP construction and zero-sum allocation | Detective | Monthly | P-04 | `RPT-015` allocation sum check |
| `CTL-022` | Nostro reconciliation and break escalation | Detective | Daily | P-04 | `RPT-027` ageing |
| `CTL-023` | Market risk limits and backtesting | Detective | Daily | P-01, P-13 | `RPT-017` |
| `CTL-024` | Counterparty exposure, netting evidence and settlement | Detective | Daily | P-02 | `RPT-018` netting evidence panel |
| `CTL-025` | Margin call and collateral concentration | Detective | Intraday | P-02 | `RPT-019` |
| `CTL-030` | Customer risk rating and review currency | Detective | Daily | P-07 | `RPT-022` |
| `CTL-031` | Sanctions screening completeness | Preventive | Continuous | P-07 | `RPT-023`, released-on-pending exception log |
| `CTL-032` | Alert and case service levels | Detective | Continuous | P-08 | `RPT-020` |
| `CTL-033` | Statutory filing deadlines | Preventive | Every 4 hours | P-07 | `RPT-021` countdown, overdue register |
| `CTL-034` | Monitoring rule coverage and lookbacks | Detective | Monthly | P-07 | `RPT-023`, coverage gap register |
| `CTL-035` | Fraud loss recognition and rule performance | Detective | Daily | P-09 | `RPT-024`, `RPT-025` |
| `CTL-036` | Chargeback deadline management | Preventive | Daily | P-09 | `RPT-024` chargeback section |
| `CTL-037` | Payment processing and exception handling | Detective | Hourly | P-06 | `RPT-026` |
| `CTL-038` | Channel availability and journey integrity | Detective | Continuous | P-10 | `RPT-032` |
| `CTL-039` | Complaint capture and conduct signal | Detective | Weekly | P-10 | `RPT-033` |
| `CTL-040` | Journal integrity and segregation of duties | Preventive | Continuous | P-06 | `RPT-028` control exception panel |
| `CTL-041` | Subledger, GL and intercompany reconciliation | Detective | Monthly | P-06 | `RPT-029` |
| `CTL-042` | Close governance and critical path | Detective | Continuous during close | P-06 | `RPT-028` |
| `CTL-043` | Party golden record and merge governance | Detective | Daily | P-12 | `RPT-038` duplicate panel |
| `CTL-044` | Operational risk capture and KRI governance | Detective | Monthly | P-01 | `RPT-037` |
| `CTL-045` | Audit finding and three-lines governance | Detective | Monthly | P-14 | `RPT-036` |
| `CTL-050` | Data quality rule execution | Detective | Every pipeline cycle | P-12 | `RPT-038` |
| `CTL-051` | Cross-system reconciliation before publication | Preventive | Every publication | P-12 | `RPT-038`, `RPT-029` |
| `CTL-052` | Single metric definition enforcement | Detective | Weekly | P-12 | Duplicate implementation scan results |
| `CTL-053` | Freshness and late arrival handling | Detective | Continuous | P-12 | `RPT-038` freshness panel |
| `CTL-054` | Restatement classification and disclosure | Preventive | Per restatement | P-12 | Restatement register with class, approval and quantified impact |
| `CTL-055` | Currency translation verification | Detective | Daily | P-12 | `BR-DQ-011` results |
| `CTL-060` | Regulatory submission governance | Preventive | Per submission | P-05 | `RPT-009`, validation results, sign-off record |
| `CTL-061` | Submission snapshot immutability and reproducibility | Preventive | Per submission | P-05 | Reproduction test result per snapshot |

### 2.1 Control design principles

- A **preventive** control stops the event. A **detective** control finds it afterwards. Where both are possible, both exist, because a preventive control that fails silently is worse than none.
- Every control produces evidence that a person other than its operator can inspect without asking the operator for it. A control whose only evidence is an assertion is not a control, per `BR-AUD-002`.
- Every control names one accountable persona. Shared accountability is no accountability.
- A control operating on data whose quality score is below its own threshold is reported as inconclusive, not as passing.

---

## 3. SAR confidentiality, in detail

This gets its own section because it is the only requirement in the document set whose violation is a criminal matter rather than a control weakness.

### 3.1 The rule

Under 31 CFR 1020.320(e), no person may disclose a suspicious activity report, or any information that would reveal its existence, other than to those permitted. This extends to the fact that a report was **considered**, not only that one was filed.

### 3.2 What this means for the platform

| Vector | Requirement |
|---|---|
| Direct columns | `sar_filed_flag`, `sar_filing_date` and the whole of `fraud.sar_filing` are hidden, not masked, for every class other than `ENT-3` and `ENT-6` |
| Row exclusion | SAR-related rows in `compliance.aml_case` are excluded from result sets, not returned with nulls |
| Bronze layer | The restriction applies from the moment of landing, per `DC-018`. There is no window in which raw AML data is broadly readable |
| Derived fields | Every derived field is assessed for whether it permits inference. An account restriction whose only possible cause is a SAR discloses the SAR |
| Aggregates | Counts are suppressed below a minimum of 20 subjects, because a count of one in a small cell identifies the subject |
| Report design | `RPT-031` omits AML data entirely rather than masking it, because a masked column tells the RM there is something to mask |
| Model features | No model consumed by an `ENT-4` persona may use a SAR-derived feature, directly or as a proxy |
| Exports and downloads | Carry the same restriction. `UR-08` exists partly for this |
| Logs and errors | An access denial message must not reveal that the denied object was SAR-related |
| Support access | Platform engineers hold no standing access. Break-glass access to AML data requires P-07 approval, is time-boxed, is logged and is reviewed |

### 3.3 Verification

`CTL-011` is tested quarterly by P-14 through an attempted-access exercise across every entitlement class and every report, including exports. The test result is an artefact retained for ten years. A single successful disclosure to a class other than `ENT-3` or `ENT-6` is a reportable regulatory incident, regardless of intent or of whether anyone actually read it.

---

## 4. BCBS 239 evidence

The supervisory finding that drove this programme was on risk data aggregation. Compliance is evidenced by artefacts, never by assertion. This table is the evidence index.

| Principle | Requirement | Evidence artefact |
|---|---|---|
| 1 Governance | Data aggregation is subject to board-level governance | Programme charter approval in [00, section 11](./00-programme-charter-and-scope.md#11-approval); CDO accountability; `RPT-039` |
| 2 Data architecture | Integrated taxonomy and architecture | The single `banking_ecm` model; conformed dimensions in [05, section 3](./05-semantic-layer-and-metrics.md#3-conformed-dimensions); `ARCH-01` to `ARCH-05` |
| 3 Accuracy and integrity | Aggregation is accurate and reconciled | `BR-DQ-004` reconciliation set; `MET-050`; `RPT-038`; `CTL-051` |
| 4 Completeness | All material risk data is captured across the group | `DC-001` to `DC-026` register; completeness thresholds in `BR-DQ-006`; the `UNCLASSIFIED` bucket controls in `BR-CRR-005` |
| 5 Timeliness | Data is available in time for decisions, including under stress | Latency classes in [03, Appendix B](./03-reporting-requirements.md#appendix-b--latency-classes); freshness SLOs in [04, section 5](./04-data-contracts-and-slos.md#5-freshness-service-level-objectives); `BR-DQ-012` |
| 6 Adaptability | Ad-hoc requests can be met, including in stress | `BR-REG-008` four-hour objective; programme objective O3; the capability gap log |
| 7 Accuracy of reporting | Reports reconcile and are reproducible | `UR-04`; `ARCH-04`; `BR-REG-004`; the as-reported serving mode in [05, section 6](./05-semantic-layer-and-metrics.md#6-bitemporal-serving) |
| 8 Comprehensiveness | Reports cover all material risk areas | The 40 report specifications against the 19 domains; the report-to-persona matrix |
| 9 Clarity and usefulness | Reports are clear and support decisions | Persona decision rights in [01](./01-personas-and-service-model.md); `UR-07`; `UR-10` |
| 10 Frequency | Frequency matches the risk and the decision | Cadence per report; `RPT-012` daily; `RPT-021` four-hourly |
| 11 Distribution | Reports reach the right people with the right access | Entitlement classes in section 1; the report-to-persona matrix |
| 12–14 Supervisory | Supervisors can review, act and cooperate | `RPT-039`; frozen snapshots under `BR-REG-004`; the ad-hoc service level under `BR-REG-008` |

Principles 3, 5 and 6 were the subject of the 2025 finding and carry additional quarterly attestation on `RPT-039`.

---

## 5. Lineage

| Requirement | Statement |
|---|---|
| `LIN-01` | Lineage is generated from deployed pipeline code and metric definitions. Hand-maintained lineage is prohibited, because it is wrong within a quarter and its wrongness is invisible |
| `LIN-02` | Lineage resolves to column grain, not table grain, for every critical data element |
| `LIN-03` | Lineage is queryable in both directions. From a published figure to its sources, and from a source column to every figure that depends on it |
| `LIN-04` | Impact analysis is a query, not an exercise. "If `DC-021` fails tonight, which reports are affected and which have regulatory deadlines" must return in seconds |
| `LIN-05` | Lineage includes model dependencies via `BR-MDL-005`, so that a model failure resolves immediately to the affected metrics |
| `LIN-06` | Lineage is versioned. Lineage as at a prior date is reproducible, because a supervisory question about a prior submission is a question about the prior pipeline |

---

## 6. Retention

| Data class | Retention | Basis |
|---|---|---|
| Regulatory submission snapshots | Longer of supervisory requirement and 10 years | `BR-REG-004` |
| Board-reported figures and packs | 10 years | Corporate governance |
| Financial crime records, alerts, cases, filings | 10 years from closure | BSA and AML rules |
| Credit exposure and impairment | 10 years | Prudential and audit |
| Ledger and reconciliation | 10 years | SOX and statutory |
| Audit findings and evidence | 10 years | Internal audit charter |
| Model documentation, validation and performance | 10 years or 5 years after retirement, whichever is longer | Model risk policy |
| Customer identity and KYC | 5 years after relationship end | AML rules |
| Payment and account transactions | 7 years | Statutory |
| Channel session and interaction detail | 90 days at full grain, 3 years aggregated | Operational need and data minimisation |
| Data quality rule results | 3 years detailed, 7 years aggregated | Control evidence |
| Access logs | 7 years | Security and `CTL-011` verification |

Retention conflicts with an erasure request are resolved in favour of retention, and the constraint is recorded and communicated to the data subject, per `BR-CUS-003`. Silent non-erasure is prohibited.

---

## 7. Change control

| Change | Approval | Additional requirement |
|---|---|---|
| `C0` metric | Metric owner | None |
| `C1` metric | Metric owner and P-12 | Consuming report owners notified |
| `C2` metric | Metric owner, P-12, and the executive owner of the consuming board report | Restatement assessment under `BR-DQ-009` |
| `C3` metric | Metric owner, P-12, P-05, and P-01 or P-06 as applicable | Restatement assessment; supervisor notification assessment; P-14 non-objection |
| Business rule (`BR-`) | The rule's approving persona per [02](./02-business-specifications.md) and P-12 | Impact analysis across all consuming reports |
| Data contract (`DC-`) | P-12 and the source owner | Notice period per [04, section 6](./04-data-contracts-and-slos.md#6-change-management-for-contracts) |
| Entitlement class (`ENT-`) | P-12 and P-14 non-objection | Attempted-access re-test before deployment |
| Control (`CTL-`) | The control owner and P-14 | Evidence design reviewed before deployment |
| Report specification (`RPT-`) | The report owner and P-12 | Acceptance criteria updated in [07](./07-acceptance-criteria-and-test-plan.md) |

### 7.1 Emergency change

An emergency change may bypass the notice period but never the approval. It requires: a named executive accepting the risk, a retrospective full approval within five business days, and an automatic entry on `RPT-036` as a control observation. An emergency change that is not retrospectively approved is reversed.

There is no emergency path that bypasses `CTL-011`. Ever.

---

## 8. Access review

| Review | Frequency | Owner | Scope |
|---|---|---|---|
| Entitlement class membership | Quarterly | P-12 with each persona owner | Every person and service principal, recertified individually |
| Time-boxed elevations | Monthly | P-12 | All grants, with evidence that each expired |
| `ENT-3` membership | Monthly | P-07 | Tightest review in the estate, because of `CTL-011` |
| `ENT-6` access log | Quarterly | P-12 | Every audit access, reviewed for scope consistency with an active engagement |
| Break-glass usage | Per event, plus monthly summary | P-12 and P-14 | Purpose, approver, duration and what was accessed |
| Orphaned access | Monthly | P-12 | Accounts with no matching active employee in `DC-025` |

A recertification that is not completed by its deadline results in access suspension, not in a reminder. This is the only mechanism that makes recertification actually happen.
