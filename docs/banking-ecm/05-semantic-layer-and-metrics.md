# 05 — Semantic Layer and Certified Metrics

**Document ID:** OAFG-BSR-2026-05 · **Version:** 1.0 · **Owner:** Chief Data Officer (P-12) · **Co-owner per metric:** as stated

---

## 1. Purpose

The semantic layer exists so that a number means the same thing everywhere. It has one job, and it fails the moment a second implementation of any metric appears anywhere in the estate.

Three rules govern it, and they are not negotiable.

| Rule | Statement |
|---|---|
| `SEM-01` | A certified metric is defined once, in the Gold layer, and every consumer references it. Restating a formula in a report, a dashboard, a notebook or a downstream tool is a defect under `BR-DQ-007`. |
| `SEM-02` | A metric carries its owner, its model dependencies, its source contracts and its consuming reports as queryable metadata, not as documentation. |
| `SEM-03` | A change to a certified metric follows the change-control path in [06, section 7](./06-governance-security-and-controls.md#7-change-control), and triggers a restatement assessment under `BR-DQ-009`. |

## 2. Certification levels

| Level | Meaning | Who may use it |
|---|---|---|
| `C3 Regulatory` | Fit for supervisory submission and public disclosure | Everyone. Change requires P-05, P-12 and the executive owner |
| `C2 Board` | Fit for board and executive reporting | Everyone. Change requires P-12 and the executive owner |
| `C1 Management` | Fit for internal management reporting | Everyone. Change requires the metric owner and P-12 |
| `C0 Analytical` | Exploratory, not certified | Analysts only, and never on a scheduled report |

A `C0` metric may never appear on any report in [03](./03-reporting-requirements.md). Promotion from `C0` requires a full certification review.

---

## 3. Conformed dimensions

Every certified metric is sliceable by these dimensions and by no others without an extension request. Conformance means one definition of "legal entity" across risk, finance and compliance, which is the thing that most often does not hold in a bank.

| ID | Dimension | Grain | Source of truth | Slowly changing |
|---|---|---|---|---|
| `DIM-001` | Legal entity | One row per legal entity | `ledger.legal_entity` | Type 2 |
| `DIM-002` | Consolidation level | Solo, sub-consolidated, group | Enumerated, governed by P-05 | Static |
| `DIM-003` | Line of business | `RETAIL`, `WHOLESALE`, `WEALTH`, `CORP` | `ledger.profit_center` hierarchy | Type 2 |
| `DIM-004` | Party | One row per party | `customer.party` | Type 2 |
| `DIM-005` | Connected client group | One row per group, derived per `BR-CRR-003` | `customer.relationship_hierarchy` | Type 2 |
| `DIM-006` | Portfolio segment | Retail mortgage, retail unsecured, SME, corporate IG, corporate sub-IG, sovereign and bank | `risk.risk_ecl_provision.portfolio_segment` | Static |
| `DIM-007` | Product type | One row per product | `reference.product_type` | Type 2 |
| `DIM-008` | Industry | NACE and NAICS, both retained | `reference.industry_code` | Type 2 |
| `DIM-009` | Geography | Country, region, and risk-country where different from booking country | `reference.country`, `reference.geographic_region` | Type 2 |
| `DIM-010` | Currency | ISO 4217 | `reference.currency` | Static |
| `DIM-011` | Date | Calendar and business day, per `DIM-012` calendars | Generated | Static |
| `DIM-012` | Calendar | Named business calendars per jurisdiction | `reference.holiday_calendar`, `reference.holiday_date` | Type 2 |
| `DIM-013` | IFRS 9 stage | 1, 2, 3, POCI | Enumerated, per `BR-IMP-002` to `BR-IMP-004` | Static |
| `DIM-014` | Internal rating | Master scale grade | `risk.counterparty_rating` | Type 2 |
| `DIM-015` | Channel | One row per channel | `channel.channel` | Type 2 |
| `DIM-016` | Employee | One row per employee | `hr.employee` | Type 2 |
| `DIM-017` | GL account | One row per account | `ledger.gl_account`, `ledger.chart_of_accounts` | Type 2 |
| `DIM-018` | Regulatory taxonomy | Return, schedule, line item | `reference.regulatory_taxonomy`, `reference.reporting_code` | Type 2 |
| `DIM-019` | Basel event type | Category and level 2 | Enumerated | Static |
| `DIM-020` | Model | One row per model per version | `risk.irb_model`, `risk.model_deployment` | Type 2 |

### 3.1 Dimension conformance rules

- A metric that cannot be sliced by `DIM-001` and `DIM-011` cannot be certified. Everything is reportable by entity and by date.
- `DIM-009` distinguishes **booking country** from **risk country**. Concentration under `BR-CRR-005` uses risk country. Regulatory returns use whichever the return specifies, and the report states which.
- `DIM-005` is derived, not sourced. Its derivation is `BR-CRR-003` and it is materialised, versioned and bitemporal, because a group structure as at a prior date must be reproducible.
- `DIM-006` values are fixed by the SICR threshold table in `BR-IMP-002`. Adding a segment requires new thresholds and is a `C3` change.

---

## 4. Certified metric register

Every metric states: identifier, name, certification level, owner, definition, grain of computation, source, dependencies and the reports that consume it. **These are the only definitions. No report restates them.**

### 4.1 Capital and leverage

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-001` | CET1 ratio | `C3` | P-04 |

Common equity tier 1 capital divided by total risk-weighted assets, at a stated consolidation level, expressed as a percentage to four decimal places before comparison to any minimum. Computed per `BR-CAP-001` from `treasury.capital_ratio.cet1_capital_amount` and the sum of credit, market and operational RWA. Never taken as a stored ratio. Consumed by RPT-001, RPT-009, RPT-014, RPT-016.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-002` | Total risk-weighted assets | `C3` | P-04 |

The sum of `credit_rwa_amount`, `market_rwa_amount` and `operational_rwa_amount` on `treasury.capital_ratio`, after application of the output floor per `BR-CAP-004`. Both the pre-floor and post-floor values are retained and the floor uplift is reportable. Consumed by RPT-001, RPT-009, RPT-016.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-003` | Credit risk-weighted assets | `C3` | P-04 |

The sum of `risk.credit_exposure.rwa_credit` over the `BR-CRR-001` population, computed per `BR-CAP-003` with approach eligibility applied per `BR-CAP-007`. Reconciles to `treasury.capital_ratio.credit_rwa_amount` within 0.05 % per `BR-DQ-004` reconciliation 4. Consumed by RPT-003, RPT-009, RPT-016.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-004` | Leverage ratio | `C3` | P-04 |

Tier 1 capital divided by total leverage exposure per `BR-CAP-005`. Leverage exposure uses leverage-specific credit conversion factors, which differ from those in `MET-003`. Consumed by RPT-001, RPT-009, RPT-014, RPT-016.

### 4.2 Liquidity and funding

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-005` | Liquidity coverage ratio | `C3` | P-04 |

High quality liquid assets after caps and haircuts divided by net cash outflows over 30 days, per `BR-LIQ-001`, at a stated entity, currency and consolidation level. Level 2 caps are applied 2B then 2A. The inflow cap of 75 % is applied at the level of reporting. Always published with its `data_quality_score`. Consumed by RPT-001, RPT-012, RPT-014, RPT-016.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-006` | Net stable funding ratio | `C3` | P-04 |

Available stable funding divided by required stable funding per `BR-LIQ-002`. Consumed by RPT-001, RPT-012, RPT-013, RPT-014, RPT-016.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-007` | HQLA composition | `C3` | P-04 |

Level 1, level 2A and level 2B amounts before and after caps and haircuts, split by encumbrance, from `treasury.liquidity_ratio` and `treasury.hqla_inventory`. Reported as a composition, never as a single total, because the composition is what constrains action. Consumed by RPT-012.

### 4.3 Credit quality and impairment

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-008` | Expected credit loss balance | `C3` | P-02 |

Total impairment provision per `BR-IMP-005`, on the basis applicable to the reporting entity per `BR-IMP-001`, after approved overlays per `BR-IMP-008`. Model output, overlay and final are separately retained and are never collapsed into a single reported figure. Consumed by RPT-001, RPT-004, RPT-005, RPT-009, RPT-016.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-009` | ECL coverage ratio | `C2` | P-02 |

`MET-008` divided by gross carrying amount, computed by stage and by segment. Group coverage on its own is not decision-useful and is always accompanied by the stage split. Consumed by RPT-001, RPT-004.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-010` | Stage 2 migration rate | `C2` | P-02 |

Balance migrating from stage 1 to stage 2 in the period, over opening stage 1 balance, per `BR-IMP-002`. Reported with the trigger split: quantitative, qualitative, and 30-day backstop. The backstop-only proportion is a required companion figure. Consumed by RPT-001, RPT-004, RPT-005.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-011` | Non-performing loan ratio | `C3` | P-02 |

Non-performing exposure per `BR-CRR-010`, including obligor contagion, over total exposure. The contagion effect is separately quantified because it is the part most often omitted. Consumed by RPT-001, RPT-004, RPT-009.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-012` | NPL coverage ratio | `C3` | P-02 |

Provision held against non-performing exposure over non-performing exposure. Consumed by RPT-001, RPT-004.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-013` | Cost of risk | `C2` | P-02 |

Impairment charge for the period, annualised, over average gross loans, in basis points. The charge excludes recoveries of previously written-off amounts, which are reported separately per `BR-IMP-012`. Consumed by RPT-001, RPT-004, RPT-030.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-014` | Net charge-off rate | `C3` | P-02 |

Charge-offs less recoveries, annualised, over average gross loans. Charge-offs are recognised in the period of the event and recoveries in the period received, per `BR-IMP-012`. Consumed by RPT-001, RPT-004, RPT-008.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-015` | Exposure-weighted average probability of default | `C2` | P-02 |

Sum of `pd × ead` over sum of `ead`, across the `BR-CRR-001` population, computed within a segment and never across segments with different PD definitions. Consumed by RPT-005, RPT-003.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-016` | Exposure-weighted downturn loss given default | `C2` | P-02 |

Sum of `lgd × ead` over sum of `ead`, using the downturn LGD where the regulatory approach requires it. Consumed by RPT-003, RPT-005.

### 4.4 Concentration and limits

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-017` | Large exposure utilisation | `C3` | P-02 |

Connected client group EAD as a percentage of eligible tier 1 capital, per `BR-CRR-004`. Reported per group, not per legal entity, and never netted across groups. Consumed by RPT-001, RPT-003, RPT-009.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-018` | Concentration Herfindahl-Hirschman index | `C2` | P-02 |

Sum of squared exposure shares within a dimension, scaled by 10,000, per `BR-CRR-005`. Computed for each of five dimensions and six dimension pairs. The `UNCLASSIFIED` bucket is always in the denominator. Consumed by RPT-001, RPT-003.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-019` | Limit utilisation | `C2` | P-01 |

Current utilisation over limit amount, computed in the limit's own currency and on the limit's own `utilization_basis`, per `BR-CRR-011`. Utilisation driven by foreign exchange movement is separately identified. Consumed by RPT-002, RPT-003, RPT-017.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-020` | Risk appetite status | `C2` | P-01 |

The red, amber or green band of an appetite metric, derived by comparing the actual value to its thresholds in the direction's sense, per `BR-CRR-012`. A metric with a null threshold in the relevant band produces no status and instead produces a governance exception. Consumed by RPT-001, RPT-002.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-021` | Covenant breach rate | `C1` | P-03 |

Effective breaches over covenants tested in the period, per `BR-CRR-013`. Reporting breaches, where the test could not be performed, are counted and reported separately and never folded in. Consumed by RPT-007, RPT-003.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-022` | Undrawn commitment and conversion | `C3` | P-02 |

Committed less drawn, and the EAD contribution after the applicable credit conversion factor per `BR-CRR-006`. Both the undrawn amount and the converted amount are reported, because they answer different questions. Consumed by RPT-003, RPT-010.

### 4.5 Profitability

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-023` | Risk-adjusted return on capital | `C2` | P-06 |

Risk-adjusted net income over allocated regulatory capital, per `BR-CAP-008`. Risk-adjusted net income is revenue less direct cost, less allocated cost, less FTP, less expected loss. Using actual impairment rather than expected loss produces a volatile and misleading figure and is prohibited. Consumed by RPT-015, RPT-030, RPT-031.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-024` | Net interest margin | `C2` | P-06 |

Net interest income over average interest-earning assets, annualised. Consumed by RPT-014, RPT-030.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-025` | FTP-adjusted contribution margin | `C2` | P-04 |

Revenue less FTP charge or credit, less direct cost, per `BR-LIQ-006`. The five FTP components are always available alongside the total. Consumed by RPT-014, RPT-015, RPT-030, RPT-031.

### 4.6 Operational and non-financial risk

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-026` | Operational risk loss | `C3` | P-01 |

Gross loss, recoveries, insurance recoveries and net loss per `BR-ORX-001`, by Basel event type and business line. Boundary events are flagged and excluded from aggregate credit or market loss to prevent double counting. Consumed by RPT-001, RPT-037.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-027` | Key risk indicator breach count | `C2` | P-01 |

Count of KRIs in amber and in red, per `BR-ORX-002`, with the count on flagged data reported separately from the count on clean data. Consumed by RPT-001, RPT-037.

### 4.7 Financial crime

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-028` | Alert to case conversion rate | `C1` | P-08 |

Alerts escalated to case over alerts dispositioned, by monitoring rule and by alert type, per `BR-AML-006`. Consumed by RPT-020.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-029` | Filing timeliness | `C3` | P-07 |

Filings made within the statutory deadline over filings due, per `BR-AML-007`, with the clock running from `detection_date`. Any figure below 100 % represents a regulatory breach and is escalated, not merely trended. Consumed by RPT-001, RPT-020, RPT-021. Subject to `BR-AML-008`.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-030` | KYC periodic review overdue rate | `C2` | P-07 |

Reviews past `next_review_due_date` over reviews due, per `BR-AML-002`, always split by risk rating and by transacting versus dormant. Consumed by RPT-001, RPT-022.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-031` | Sanctions screening false positive rate | `C2` | P-07 |

Hits dispositioned as false positive over total hits, by list and by matching algorithm, per `BR-AML-004`. A rate above 98 % on any list is an effectiveness concern, not a success. Consumed by RPT-023.

### 4.8 Fraud

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-032` | Net fraud loss rate | `C2` | P-09 |

Net loss in basis points of transaction throughput, by channel and typology, per `BR-FRD-001`. Loss is recognised in the period of the event, recovery in the period received. Consumed by RPT-001, RPT-024.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-033` | Detection precision and value missed | `C1` | P-09 |

True positive alerts over total alerts, and the value of confirmed fraud with no prior alert, per `BR-FRD-002`. Never compared across a rule version change without the change being marked. Consumed by RPT-024, RPT-025.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-034` | Chargeback ratio | `C1` | P-09 |

Chargeback count and value over transaction count and value, by merchant, per `BR-FRD-004`, measured against network thresholds. Consumed by RPT-024.

### 4.9 Payments and channels

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-035` | Straight-through processing rate | `C1` | P-06 |

Payments completing with no intervention over payments initiated, per `BR-PAY-001`, by type, channel, currency and corridor. Automated repair disqualifies a payment and is counted separately from manual repair. A single group figure does not satisfy this metric. Consumed by RPT-026.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-036` | Payment exception ageing | `C1` | P-06 |

Open exceptions by age band and by time remaining to cut-off, per `BR-PAY-002`. Time to cut-off takes priority over age in ordering. Consumed by RPT-026.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-037` | Settlement fail rate | `C2` | P-06 |

Trades unsettled on contractual settlement date over trades due, per `BR-MKT-004`, split by cause attribution between counterparty and OAFG. Consumed by RPT-017, RPT-026.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-038` | Nostro break ageing | `C2` | P-04 |

Unmatched items by age from value date, in bands of 0–1, 2–5, 6–30 and over 30 days, per `BR-LIQ-007`. Items over 30 days feed `MET-026`. Consumed by RPT-027, RPT-037.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-044` | Channel availability | `C1` | P-10 |

Uptime percentage and customer-impacting minutes, per `BR-CHN-001`. Customer-impacting minutes weight downtime by the sessions that would have occurred based on the equivalent interval in the prior four weeks. Uptime percentage alone does not satisfy this metric. Consumed by RPT-032.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-045` | Onboarding cycle time | `C1` | P-10 |

Elapsed time from journey start to completion, per `BR-CHN-002`, with time waiting on the customer shown separately from time within OAFG's control. Consumed by RPT-032, RPT-008.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-046` | Complaint rate and resolution timeliness | `C2` | P-10 |

Complaints normalised by product holdings, and the proportion resolved within the regulatory deadline, per `BR-CHN-003`. Raw counts do not satisfy this metric. Consumed by RPT-033.

### 4.10 Finance and close

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-039` | Days to close and critical path | `C1` | P-06 |

Working days from period end to sign-off, and the current critical path length during an open close, per `BR-FIN-004`. Consumed by RPT-028.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-040` | Reconciliation variance | `C3` | P-06 |

Absolute difference between reconciled populations, by reconciliation, with materiality position per `MAT-03` and ageing, per `BR-FIN-003` and `BR-DQ-004`. Consumed by RPT-028, RPT-029, RPT-038.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-041` | Manual journal ratio | `C2` | P-06 |

Manual journals over total journals, by count and by absolute value, per `BR-FIN-002`, with late-period high-value entries listed individually rather than aggregated. Consumed by RPT-028.

### 4.11 Customer

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-042` | Net promoter score | `C1` | P-10 |

From `customer.party.nps_score`, aggregated with a minimum response threshold of 30 per reported cell. Cells below the threshold are suppressed rather than reported with a wide confidence interval. Consumed by RPT-031, RPT-032.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-043` | Customer lifetime value | `C1` | P-10 |

From `customer.party.cltv_score`. This is a model output and is subject to `BR-MDL-001`. It is never used for adverse customer decisions, only for service prioritisation. Consumed by RPT-031.

### 4.12 Model risk and data quality

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-047` | Model validation overdue rate | `C2` | P-13 |

Models past `next_validation_date` over models in scope, per `BR-MDL-002`, weighted separately by count and by the regulatory materiality of the metrics they feed via `BR-MDL-005`. Consumed by RPT-001, RPT-034.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-048` | Model override rate | `C2` | P-13 |

Valid overrides over model outputs, by model, direction, analyst and approver, per `BR-CRR-008` and `BR-IMP-011`. Invalid overrides, those missing direction, reason or approval, are counted separately and are a control failure rather than a rate. Consumed by RPT-034, RPT-035.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-049` | Audit issue ageing | `C2` | P-14 |

Open findings and management actions by days past due, rating and owner, per `BR-AUD-001`, with extension count. Consumed by RPT-001, RPT-036.

| ID | Metric | Level | Owner |
|---|---|---|---|
| `MET-050` | Data quality score | `C3` | P-12 |

Weighted proportion of quality rules passing per `BR-DQ-013`, weights 5 for blocking, 3 for qualifying, 1 for advisory, capped at 0.80 while any blocking rule fails. Published on every report per `UR-02`. Consumed by every report.

---

## 5. Metric metadata contract

Every certified metric exposes the following as queryable metadata. This is what makes `BR-MDL-005` and `RPT-039` possible.

| Attribute | Content |
|---|---|
| `metric_id` | `MET-nnn` |
| `certification_level` | `C0` to `C3` |
| `owner_persona` | The accountable persona |
| `definition_version` | Incremented on every change |
| `effective_from`, `effective_to` | The period this version applies to |
| `business_rules` | The `BR-` rules that govern it |
| `source_contracts` | The `DC-` contracts it depends on |
| `model_dependencies` | The `DIM-020` model versions it depends on, transitively |
| `conformed_dimensions` | The `DIM-` dimensions it is sliceable by |
| `consuming_reports` | The `RPT-` specifications that use it |
| `change_control_reference` | The approval record for the current version |
| `quality_gate` | The `MET-050` threshold below which it must not publish |

A metric missing any of these attributes cannot be certified above `C0`. The metadata is generated from the deployed definition, not maintained separately, because separately maintained metadata is wrong within a quarter.

---

## 6. Bitemporal serving

Every `C2` and `C3` metric is served in three modes, per [00, section 6](./00-programme-charter-and-scope.md#6-bitemporality).

| Mode | Parameters | Use |
|---|---|---|
| Current | `as_of_date` | Management reporting. Default |
| As-reported | `as_of_date`, `knowledge_date` | Reproducing a submission, a Board pack or an audit position |
| Restatement delta | `as_of_date`, two `knowledge_date` values | The difference, attributed by `BR-DQ-009` class |

A metric that cannot serve as-reported mode cannot be certified `C3`. This is the mechanism by which P-05's defining requirement is met, and it is enforced at certification rather than discovered at submission.

---

## 7. Extension requests

New metrics and new dimensions are requested through the change-control path. A request must state:

1. The decision the metric supports and the persona who makes it
2. Why no existing certified metric answers the question, which is usually the point at which the request is withdrawn
3. The proposed definition, at the same level of precision as those in section 4
4. The source contracts and model dependencies
5. The proposed certification level and the owner willing to be accountable for it

Requests without a named accountable owner are rejected. A metric nobody owns is a metric nobody will fix.
