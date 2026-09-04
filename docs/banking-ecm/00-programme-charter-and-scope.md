# 00 — Programme Charter, Scope and Glossary

**Document ID:** OAFG-BSR-2026-00 · **Version:** 1.0 · **Owner:** Group Chief Data Officer (P-12) · **Approver:** Group Executive Committee

---

## 1. The institution

OctoAcme Financial Group (OAFG) is a universal banking group. The specification assumes the following organisational shape, because every reporting rule in this set is scoped by legal entity, consolidation level and supervisory regime.

### 1.1 Legal entity hierarchy

| Entity code | Legal entity | Consolidation role | Primary supervisor | Functional currency |
|---|---|---|---|---|
| `OAFG-HLD` | OctoAcme Financial Group Holdings | Top consolidated group | Federal Reserve (IHC) | USD |
| `OA-BNA` | OctoAcme Bank, N.A. | US insured depository | OCC / FDIC | USD |
| `OA-BEU` | OctoAcme Bank Europe S.A. | EU credit institution | ECB (SSM) via CBI | EUR |
| `OA-SEC` | OctoAcme Securities Ltd | UK investment firm | PRA / FCA | GBP |
| `OA-WAG` | OctoAcme Wealth AG | Swiss private bank | FINMA | CHF |
| `OA-SPV` | OctoAcme Funding SPV I–IV | Securitisation vehicles | n/a (consolidated) | USD |

These map to `banking_ecm.ledger.legal_entity`. Every risk, finance and regulatory measure in this specification is reportable at **solo**, **sub-consolidated** and **group-consolidated** levels, controlled by `consolidation_level` on `treasury.capital_ratio` and `treasury.liquidity_ratio` and by `consolidation_scope` on `risk.liquidity_metric`.

### 1.2 Business divisions

Three divisions, mapped to `line_of_business` codes used consistently across `risk.appetite`, `risk.risk_limit`, `treasury.ftp_rate` and `risk.concentration_risk`:

| LOB code | Division | Principal ECM domains |
|---|---|---|
| `RETAIL` | Retail & Business Banking | `account`, `channel`, `customer`, `payment`, `loan` |
| `WHOLESALE` | Corporate & Institutional Banking | `loan`, `collateral`, `trade`, `investment`, `risk`, `treasury` |
| `WEALTH` | Wealth & Asset Management | `wealth`, `asset`, `security`, `investment` |

Corporate functions (`CORP`) cover `ledger`, `hr`, `audit`, `compliance` and `reference`.

### 1.3 Scale assumptions

These are the volumetrics the platform is sized against. They drive [08 — Non-functional requirements](./08-non-functional-requirements.md) and must be revalidated annually.

| Dimension | Volume | Growth assumption |
|---|---|---|
| Parties (`customer.party`) | 14.2 M | +6 % p.a. |
| Deposit accounts (`account.deposit_account`) | 23.6 M | +5 % p.a. |
| Loan accounts (`loan.loan_account`) | 4.1 M | +8 % p.a. |
| Wholesale facilities (`loan.facility`) | 68 K | +4 % p.a. |
| Account transactions (`account.account_transaction`) | 5.8 B rows retained | 1.9 B new rows p.a. |
| Payment transactions (`payment.payment_transaction`) | 2.4 B rows retained | 780 M new rows p.a. |
| Credit exposures (`risk.credit_exposure`) | 41 M rows per month-end snapshot | 12 monthly + 20 quarterly retained snapshots |
| ECL provision records (`risk.risk_ecl_provision`) | 4.2 M rows per reporting date | 84 reporting dates retained |
| AML alerts (`compliance.aml_alert`) | 1.1 M p.a. | +15 % p.a. |
| Fraud alerts (`fraud.fraud_alert`) | 3.7 M p.a. | +22 % p.a. |
| Concurrent named report consumers | 2,400 | 3,600 at peak close |

---

## 2. Why the programme exists

OAFG currently produces risk, finance and regulatory reporting from 31 disconnected marts. The consequences are documented and are the programme's mandate:

1. **No single version of exposure.** Credit exposure reported to the Board differs from the exposure submitted on FR Y-14Q by an unexplained 2.1 % to 3.8 % each quarter. Both numbers are defensible in isolation and neither reconciles.
2. **Impairment is manual.** IFRS 9 stage allocation for the wholesale book is decided in spreadsheets outside any controlled system. There is no reproducible audit trail from a stage assignment back to the significant-increase-in-credit-risk test that produced it.
3. **Regulatory findings are open.** A 2025 supervisory examination raised findings on risk data aggregation capability (BCBS 239 principles 3, 5 and 6), specifically the inability to produce group-consolidated credit concentration within the supervisor's requested timeframe during a stress period.
4. **Financial crime operates blind to context.** AML investigators cannot see a subject's full relationship, collateral and payment footprint in one place, so case handling time exceeds the 30-day internal SLA on 34 % of escalated cases.
5. **Data ownership is undefined.** No critical data element has a named accountable owner. When a number is wrong, no one is required to fix it.

### 2.1 Programme objectives

| Objective | Measure of success | Target | Baseline |
|---|---|---|---|
| O1 — One certified exposure figure | Absolute variance between Board-reported and regulatory-submitted credit exposure | ≤ 0.05 % | 2.1–3.8 % |
| O2 — Reproducible impairment | Proportion of IFRS 9 stage assignments traceable to a system-recorded SICR test | 100 % | ~12 % |
| O3 — Aggregation under stress | Elapsed time to produce group-consolidated concentration report on ad-hoc request | ≤ 4 hours | 9 working days |
| O4 — Financial crime context | Median AML escalated case handling time | ≤ 18 days | 31 days |
| O5 — Accountable data | Critical data elements with a named steward and a passing quality score | 100 % of 412 CDEs | 0 |
| O6 — Close acceleration | Working days to group close sign-off | 6 | 11 |

Objectives are tracked monthly on `RPT-039` and are the acceptance basis for programme completion in [09](./09-delivery-roadmap-and-raci.md).

---

## 3. Regulatory drivers

Every reporting requirement in this set traces to at least one driver below. The traceability matrix is in [07, section 8](./07-acceptance-criteria-and-test-plan.md#8-regulatory-traceability-matrix).

### 3.1 United States

| Driver | Applies to | Frequency | Principal ECM sources |
|---|---|---|---|
| FFIEC 031 Call Report | `OA-BNA` | Quarterly | `ledger`, `loan`, `account`, `risk` |
| FR Y-9C Consolidated Financial Statements | `OAFG-HLD` | Quarterly | `ledger`, `risk`, `treasury` |
| FR Y-14A / Q / M (CCAR, DFAST) | `OAFG-HLD` | Annual / quarterly / monthly | `loan`, `risk`, `collateral`, `customer` |
| FR 2052a Liquidity Monitoring | `OAFG-HLD`, `OA-BNA` | Daily | `treasury`, `account`, `payment` |
| Regulation YY enhanced prudential standards | `OAFG-HLD` | Continuous | `risk`, `treasury` |
| BSA / USA PATRIOT Act — SAR, CTR | All US entities | Event-driven | `compliance`, `fraud`, `payment` |
| 31 CFR 1020.320(e) SAR confidentiality | All US entities | Continuous | `compliance.sar_filing`, `fraud.sar_filing` |
| OFAC sanctions | Group-wide | Real time | `compliance.sanctions_screening_event` |

### 3.2 European Union and United Kingdom

| Driver | Applies to | Frequency | Principal ECM sources |
|---|---|---|---|
| CRR / CRD — COREP own funds, credit risk, large exposures | `OA-BEU` | Quarterly | `risk`, `treasury`, `loan` |
| FINREP financial reporting | `OA-BEU` | Quarterly | `ledger`, `loan`, `risk` |
| AnaCredit (ECB Regulation 2016/867) | `OA-BEU` | Monthly | `loan`, `customer`, `collateral`, `reference` |
| LCR / NSFR implementing technical standards | `OA-BEU` | Monthly / quarterly | `treasury`, `account` |
| EMIR / MiFIR transaction reporting | `OA-SEC` | T+1 | `trade`, `security`, `reference` |
| PRA110 cash flow mismatch | `OA-SEC` | Weekly | `treasury` |
| EU AML Directives (6AMLD) | `OA-BEU` | Continuous | `compliance`, `customer` |

### 3.3 Cross-cutting

| Driver | Effect on this specification |
|---|---|
| **IFRS 9** | Governs `BR-IMP-001` to `BR-IMP-012`. Drives `risk.risk_ecl_provision.ifrs9_stage`, `sicr_flag`, `ecl_12month_amount`, `ecl_lifetime_amount` |
| **ASC 326 (CECL)** | Runs in parallel for US entities. Drives `cecl_pool_classification`, lifetime loss without staging |
| **Basel III finalisation** | Output floor, revised SA and IRB. Drives `BR-CAP-001` to `BR-CAP-008` |
| **BCBS 239** | Governs the whole of [06](./06-governance-security-and-controls.md). Principles 3 (accuracy), 5 (timeliness), 6 (adaptability) are explicitly evidenced |
| **SOX 404** | `ledger.ledger_sox_control`, `compliance.compliance_sox_control`. Drives control attestation in `RPT-029` |
| **IFRS 7 / Pillar 3** | Public disclosure. `risk.credit_exposure.pillar3_disclosure_flag` |
| **GDPR / CCPA** | `customer.consent_record`, `compliance.data_subject_request`. Drives masking policy in `CTL-014` |

---

## 4. Scope

### 4.1 In scope

- All 19 `banking_ecm` schemas as the Silver layer, consumed read-only by this platform
- A Gold semantic layer of certified metrics and conformed dimensions ([05](./05-semantic-layer-and-metrics.md))
- 40 report specifications across 14 personas ([03](./03-reporting-requirements.md))
- Bitemporal history for all regulatory-submitted measures (`as_of_date` and `knowledge_date`)
- Entitlement, masking and lineage controls ([06](./06-governance-security-and-controls.md))
- Data quality measurement and remediation workflow for 412 critical data elements
- Reconciliation between risk, finance and regulatory views of the same measure

### 4.2 Out of scope

| Excluded | Rationale | Owning programme |
|---|---|---|
| Modification of source systems of record (T24, FIS Profile, Murex, Actimize) | Platform consumes, never writes back | Core Banking Modernisation |
| Regulatory submission file formatting and transmission (XBRL taxonomy binding, EBA DPM) | Handled by the existing Axiom submission layer, which consumes the Gold extracts specified here | Regulatory Technology |
| Model development and calibration | This platform stores model outputs and governs model metadata only. See `BR-MDL-001` for the boundary | Model Risk Management |
| Customer-facing statement generation | `account.statement` is a source, not a product of this platform | Retail Digital |
| Trading front-office pricing and execution | `trade` schema consumed for risk and reporting only | Markets Technology |
| Real-time transaction blocking or payment interdiction | Platform is analytical. Detection outputs feed operational systems, they do not act | Payments Engineering |

### 4.3 Explicit non-goals

The platform is **not** a system of record. If a number in the platform disagrees with the source system of record, the source wins and the platform has a defect. The single exception is a certified metric where the source disagreement is itself the finding, which is then raised under `BR-DQ-004`.

The platform does **not** make credit, fraud or compliance decisions. It presents evidence to a person who decides, and it records that a person decided. Where this specification describes a threshold that triggers something, the trigger is always a work item for a named human, never an automated adverse action against a customer.

---

## 5. Architectural context

The specification assumes a medallion architecture on Databricks with Unity Catalog as the governance plane.

```
Source systems of record
  Temenos T24, FIS Profile        core banking, party and account
  Murex, Calypso                  trading, collateral, treasury
  nCino, Loan IQ                  credit origination and servicing
  Actimize, Fircosoft             AML monitoring and sanctions screening
  Falcon, Featurespace            fraud detection
  Oracle EBS, SAP                 general ledger
  Salesforce Financial Services   CRM, relationship management
  Workday                         HR
        |
        v
BRONZE   banking_raw            append-only landing, source-fidelity, no transformation
        |
        v
SILVER   banking_ecm            the 19-schema ECM model, conformed, FK-validated, SCD2 where
                                specified in document 04. THIS SPECIFICATION'S SOURCE OF TRUTH.
        |
        v
GOLD     banking_gold           certified metric views, conformed dimensions, report-serving
                                aggregates, regulatory submission extracts, frozen snapshots
        |
        v
Consumers  Databricks SQL dashboards · Power BI semantic models · Axiom regulatory submission
           · Actimize case enrichment · ad-hoc analyst notebooks · supervisory data requests
```

### 5.1 Layer rules

| Rule | Statement |
|---|---|
| `ARCH-01` | No consumer reads Bronze. Ever. |
| `ARCH-02` | Reports read Gold. Analysts with entitlement class `ENT-2` or above may read Silver for investigation, but no scheduled report may be built on Silver. |
| `ARCH-03` | A metric exists in exactly one place in Gold. Duplicated logic is a defect, raised as `BR-DQ-007`. |
| `ARCH-04` | Gold is rebuildable from Silver, and Silver from Bronze, deterministically, for any historical `as_of_date`. Non-reproducibility is a severity-1 defect. |
| `ARCH-05` | Any measure that has ever been externally submitted is frozen as an immutable snapshot at submission and never recomputed in place. See `BR-REG-004`. |

---

## 6. Bitemporality

This is the concept most often got wrong, so it is stated once here and referenced everywhere else.

Every reportable fact carries two dates:

| Date | Meaning | Physical column convention |
|---|---|---|
| **`as_of_date`** | The business date the fact describes. "What was the exposure on 31 March?" | `measurement_date`, `reporting_date`, `metric_date`, `accounting_date` depending on domain |
| **`knowledge_date`** | The date the platform knew the fact. "What did we believe on 5 April about 31 March?" | `record_created_timestamp` / `created_timestamp` in Silver; explicit `knowledge_date` column in Gold |

Three query modes must be supported by every Gold regulatory table:

1. **Current view** — latest knowledge of a given `as_of_date`. The default for management reporting.
2. **As-reported view** — knowledge as at a stated prior `knowledge_date`. Mandatory for reproducing a submission, an audit position, or a Board pack.
3. **Restatement delta** — the difference between the two, attributed by cause. Mandatory input to `BR-DQ-009`.

A report that cannot answer "what did we submit, and why does it now differ" is not acceptable, regardless of how correct its current numbers are.

---

## 7. Currency and translation

| Rule | Statement |
|---|---|
| `FX-01` | Group reporting currency is USD. `reporting_currency_code` on `risk.credit_exposure` and `risk.concentration_risk` must be `USD` for all group-consolidated rows. |
| `FX-02` | Balance-sheet items translate at the closing rate on `as_of_date` from `reference.exchange_rate`. Income-statement items translate at the period average rate. |
| `FX-03` | Regulatory submissions translate at the rate mandated by the receiving supervisor, which may differ from `FX-02`. The rate applied is stored on the frozen submission snapshot and never re-derived. |
| `FX-04` | `risk.credit_exposure.fx_rate` and `risk.concentration_risk.fx_rate` record the rate actually applied to that row. A row whose recomputed local-to-reporting conversion differs from the stored `fx_rate` by more than 1 basis point fails `BR-DQ-011`. |
| `FX-05` | Multi-currency facilities report exposure in the facility currency and in USD. Both are retained. Aggregation is only ever performed on the USD amount. |

---

## 8. Materiality and rounding

| Rule | Statement |
|---|---|
| `MAT-01` | Group management reporting rounds to USD thousands. Regulatory submission rounds per the supervisor's instruction, applied at the last step only. |
| `MAT-02` | Rounding is applied to presentation, never to stored values. Stored monetary values are `DECIMAL(18,2)` throughout the ECM model and are used unrounded in all aggregation. |
| `MAT-03` | A reconciliation difference is **material** if it exceeds the lower of USD 250,000 or 0.10 % of the reconciled population. Material differences block sign-off. |
| `MAT-04` | A reconciliation difference below materiality is still recorded, aged, and reported on `RPT-029`. "Immaterial" never means "ignored". |
| `MAT-05` | Ratios are reported to four decimal places internally and two decimal places externally. A capital ratio is never rounded before comparison to a regulatory minimum. |

---

## 9. Glossary

Terms are defined once, here, and used consistently. Where a term has a different colloquial meaning inside OAFG, the definition below prevails for the purposes of this specification.

| Term | Definition | Principal ECM location |
|---|---|---|
| **As-of date** | The business date a fact describes | See section 6 |
| **CCF** | Credit conversion factor applied to undrawn commitment to derive EAD | Derived, `BR-CRR-006` |
| **CDE** | Critical data element. An attribute whose failure would materially misstate a board-reported or regulatory-submitted measure | `RPT-038` |
| **CET1** | Common equity tier 1 capital | `treasury.capital_ratio.cet1_capital_amount` |
| **Consolidation level** | Solo, sub-consolidated or group-consolidated reporting perimeter | `treasury.capital_ratio.consolidation_level` |
| **CVA** | Credit valuation adjustment, the market value of counterparty credit risk | `risk.credit_exposure.cva` |
| **EAD** | Exposure at default | `risk.credit_exposure.ead` |
| **ECL** | Expected credit loss under IFRS 9 | `risk.risk_ecl_provision` |
| **Entitlement class** | The access tier assigned to a persona, `ENT-1` to `ENT-7` | [06](./06-governance-security-and-controls.md) |
| **Forbearance** | A concession granted to a borrower in financial difficulty | `loan.loan_account.forbearance_flag` |
| **FTP** | Funds transfer pricing, the internal rate charged or credited for funding | `treasury.ftp_rate` |
| **Grain** | The exact meaning of one row in a report or table. Stated for every report in [03](./03-reporting-requirements.md) | — |
| **HQLA** | High quality liquid assets, levels 1, 2A and 2B | `treasury.hqla_inventory` |
| **Knowledge date** | The date the platform learned a fact | See section 6 |
| **Large exposure** | An exposure to a connected client group of 10 % or more of tier 1 capital | `risk.credit_exposure.large_exposure_flag` |
| **LCR** | Liquidity coverage ratio | `treasury.liquidity_ratio.lcr_percentage` |
| **LGD** | Loss given default | `risk.credit_exposure.lgd` |
| **NPL** | Non-performing loan | `loan.loan_account.npl_classification` |
| **NSFR** | Net stable funding ratio | `treasury.liquidity_ratio.nsfr_percentage` |
| **PD** | Probability of default, 12-month or lifetime | `risk.credit_exposure.pd`, `risk.risk_ecl_provision.pd_lifetime` |
| **POCI** | Purchased or originated credit-impaired | `risk.risk_ecl_provision.poci_flag` |
| **RAROC** | Risk-adjusted return on capital | Derived, `MET-023` |
| **RWA** | Risk-weighted assets | `risk.credit_exposure.rwa_credit`, `treasury.capital_ratio` |
| **SICR** | Significant increase in credit risk, the IFRS 9 stage 1 to stage 2 trigger | `risk.risk_ecl_provision.sicr_flag` |
| **Stage** | IFRS 9 impairment stage 1, 2 or 3 | `risk.risk_ecl_provision.ifrs9_stage` |
| **STP** | Straight-through processing, a transaction requiring no manual intervention | Derived, `MET-035` |

---

## 10. Assumptions and dependencies

| ID | Assumption | If false |
|---|---|---|
| `ASM-01` | The `banking_ecm` Silver layer is populated and FK-valid before Gold build begins each cycle | Gold build halts, `RPT-038` raises a blocking data quality event |
| `ASM-02` | Source systems deliver within the windows in [04](./04-data-contracts-and-slos.md) | Late arrival handling under `BR-DQ-012` applies, downstream latency SLOs are formally breached and reported |
| `ASM-03` | Regulatory rule interpretation is provided by Group Regulatory Policy and is not derived by the platform team | Any platform-originated interpretation is a control failure |
| `ASM-04` | Model outputs (PD, LGD, EAD, CCF) are calculated upstream and land in `risk.irb_model` and related tables | The platform does not calculate risk parameters. See `BR-MDL-001` |
| `ASM-05` | Unity Catalog is the single entitlement authority. No report tool holds its own row-level security | Duplicated entitlement logic is a `CTL-003` failure |
| `ASM-06` | Reference data (`reference` schema) is complete for all currencies, countries and instruments referenced by transactional data | Orphan FK, blocking under `BR-DQ-002` |

---

## 11. Approval

| Role | Persona | Approval scope |
|---|---|---|
| Group Chief Risk Officer | P-01 | Sections 2, 3, 4; all risk business rules |
| Chief Financial Officer | P-06 | Sections 7, 8; all finance business rules |
| Chief Compliance Officer | P-07 | Section 3; all financial crime business rules |
| Group Treasurer | P-04 | Liquidity and capital business rules |
| Chief Data Officer | P-12 | Sections 5, 6, 9, 10; the whole of documents 04 and 06 |
| Chief Audit Executive | P-14 | Observer. Does not approve, but records non-objection |
