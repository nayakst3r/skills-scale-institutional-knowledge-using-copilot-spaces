# 03 — Reporting Requirements

**Document ID:** OAFG-BSR-2026-03 · **Version:** 1.0 · **Owner:** Head of Business Analysis
**Approvers:** the owning persona of each report

---

## 0. How to read a report specification

Each specification carries the same fields. A report cannot be built from anything less.

| Field | Meaning |
|---|---|
| **Owner** | The persona accountable for the report's content. One person, never a committee. |
| **Consumers** | Other personas who read it. Their entitlement still governs what they see. |
| **Grain** | What exactly one row means. If this is ambiguous, everything downstream is wrong. |
| **Cadence** | How often it is produced |
| **Latency SLO** | The maximum elapsed time from the close of the `as_of_date` to availability |
| **Entitlement** | The minimum `ENT-n` class, plus any row or column restriction |
| **Measures** | The certified metrics used, by `MET-nnn`. Never a formula. |
| **Rules** | The `BR-` rules that must have executed for the report to be valid |
| **Quality gate** | The condition under which the report publishes, publishes qualified, or does not publish |
| **Retention** | How long each produced instance is retained and reproducible |
| **Test** | The `AC-nnn` acceptance criterion |

### 0.1 Universal requirements

Every report in this document must satisfy all of the following. They are not repeated in each specification.

| ID | Requirement |
|---|---|
| `UR-01` | Displays its `as_of_date` and its `knowledge_date` in the header, always, at equal prominence |
| `UR-02` | Displays the data quality score of every dataset it consumes, and the qualification banner where any is below threshold, per `BR-DQ-013` |
| `UR-03` | Every figure is traceable to its certified metric identifier, visible on hover or in an adjacent definition panel |
| `UR-04` | Every instance is reproducible for its retention period, per `ARCH-04` |
| `UR-05` | Applies entitlement at the Unity Catalog layer. No report tool holds its own row-level security, per `ASM-05` |
| `UR-06` | Wide tables scroll inside their own container. The page never scrolls horizontally |
| `UR-07` | Any movement measure is accompanied by its attribution, not merely its value |
| `UR-08` | Exports carry the same header, the same qualification and the same entitlement as the on-screen view |
| `UR-09` | The report names its owning persona and the date its definition was last changed |
| `UR-10` | No report displays a number it cannot explain. Where a drill path does not exist, the figure is labelled as not drillable and the gap is logged |

---

# Part A — Group risk reporting (P-01)

## RPT-001 — Board Risk Dashboard

| Field | Value |
|---|---|
| Owner | P-01 |
| Consumers | Board Risk Committee, P-02, P-04, P-06, P-07, P-14 |
| Grain | One row per board-reported risk appetite metric per reporting period |
| Cadence | Monthly, aligned to the Board Risk Committee calendar |
| Latency SLO | T+4 business days from month end |
| Entitlement | `ENT-1`. Aggregate only. Counterparty names visible only where `MET-017` identifies a large exposure |
| Retention | 10 years, fully reproducible |

**Sections.**
1. **Appetite position.** Every metric with `is_board_approved` true, its status, its threshold, its value and its trend over 13 periods.
2. **Movement explanation.** Every metric that changed status since the prior period, with the attribution required by `UR-07`.
3. **Capital and liquidity.** `MET-001`, `MET-002`, `MET-004`, `MET-005`, `MET-006`, with headroom to minimum and to buffer.
4. **Credit quality.** `MET-008`, `MET-009`, `MET-010`, `MET-011`, `MET-012`, `MET-013`.
5. **Concentration.** `MET-017`, `MET-018` across all five dimensions of `BR-CRR-005`, plus the six combination pairs.
6. **Non-financial risk.** `MET-026`, `MET-027`, `MET-029`, `MET-032`, `MET-049`.
7. **Stress.** Latest complete `BR-CAP-006` run, with `capital_action_restriction_flag` shown prominently where true.
8. **Open items.** Every red status with its required escalation and the deadline from `breach_response_timeframe_days`.

**Measures.** `MET-001` to `MET-006`, `MET-008` to `MET-014`, `MET-017` to `MET-021`, `MET-026`, `MET-027`, `MET-029`, `MET-032`, `MET-047`, `MET-049`, `MET-050`.

**Rules.** `BR-CRR-004`, `BR-CRR-005`, `BR-CRR-012`, `BR-IMP-009`, `BR-CAP-001`, `BR-CAP-002`, `BR-CAP-006`, `BR-LIQ-001`, `BR-LIQ-002`, `BR-ORX-002`.

**Quality gate.** Does not publish while any blocking rule in Appendix B of [02](./02-business-specifications.md#appendix-b--blocking-rules) is failing on a consumed dataset. Publishes qualified where a qualifying rule fails, with the affected metrics individually marked.

**Notes.** A red status must render with its required escalation on the same screen, per `BR-CRR-012`. A dashboard that shows a breach without the response it demands has failed its purpose.

**Test.** `AC-201`.

---

## RPT-002 — Risk Appetite Monitoring

| Field | Value |
|---|---|
| Owner | P-01 |
| Consumers | P-02, P-04, P-07, P-09, P-13, P-14 |
| Grain | One row per appetite metric per legal entity per line of business per measurement date |
| Cadence | Monthly, with weekly refresh for daily-measured metrics |
| Latency SLO | T+1 business day for daily metrics, T+3 for monthly |
| Entitlement | `ENT-2` |
| Retention | 10 years |

**Dimensions.** Risk category, risk sub-category, legal entity, line of business, governance body, measurement frequency, board-reported flag, regulatory-KRI flag.

**Measures.** `MET-020` status, actual value, green, amber and red thresholds, prior period value, 13-period trend, headroom in the metric's own unit and as a percentage of threshold.

**Required behaviours.**
- Metrics are grouped by governance body, because that determines who acts.
- A metric within 10 % of its amber threshold and deteriorating is highlighted before it breaches.
- Metrics whose thresholds are null, or whose `expiry_date` has passed without a successor, appear in a dedicated governance-exception panel. They are the most important rows on the report.
- Breach records carry the escalation level, the responsible authority, the response deadline and the days remaining or overdue.

**Rules.** `BR-CRR-012`, `BR-ORX-002`.

**Test.** `AC-202`.

---

## RPT-016 — Stress Test Results and Attribution

| Field | Value |
|---|---|
| Owner | P-01 |
| Consumers | P-02, P-04, P-05, P-06, P-13, P-14 |
| Grain | One row per stress test run per scenario per projection quarter per portfolio scope |
| Cadence | Quarterly internal, annual regulatory, plus ad hoc |
| Latency SLO | T+10 business days from run completion |
| Entitlement | `ENT-2` |
| Retention | 10 years, frozen per `BR-REG-004` where submitted |

**Sections.**
1. **Run inventory.** Every run with its status, scenario, scope, model versions, executor and approver. Incomplete runs are listed but their results are suppressed, per `BR-CAP-006`.
2. **Capital trajectory.** Stressed CET1, tier 1, total capital and leverage by projection quarter, against minima and buffers, with the trough quarter identified.
3. **Loss drivers.** Stressed ECL, PPNR, net interest income impact, RWA migration, CVA, VaR.
4. **Liquidity under stress.** Stressed LCR and NSFR, survival horizon.
5. **Attribution.** Change from the prior run decomposed into portfolio change, scenario change, model change and methodology change.
6. **Capital actions.** Planned dividends and buybacks against the maximum distributable amount, with `capital_action_restriction_flag`.

**Measures.** `MET-001` to `MET-006` in stressed form, `MET-008`, `MET-002`.

**Rules.** `BR-CAP-006`, `BR-CAP-002`, `BR-IMP-006`, `BR-MDL-004`.

**Quality gate.** A run whose `run_status` is not complete cannot contribute a result figure anywhere on this report. Suppression must be visible, not silent.

**Test.** `AC-203`.

---

# Part B — Credit portfolio reporting (P-02, P-03)

## RPT-003 — Portfolio Concentration and Large Exposure

| Field | Value |
|---|---|
| Owner | P-02 |
| Consumers | P-01, P-03, P-05, P-14 |
| Grain | One row per concentration dimension value per legal entity per consolidation level per measurement date |
| Cadence | Weekly, with daily refresh for the large exposure section |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-2`. Counterparty legal name visible; party PII masked |
| Retention | 7 years |

**Sections.**
1. **Large exposures.** Every connected client group at or above 10 % of tier 1, per `BR-CRR-004`, with group composition, aggregate EAD, percentage of tier 1, limit, headroom and trend. Groups between 8 % and 10 % appear as approaching.
2. **Single-name concentration.** Top 50 connected groups by EAD, with rating, stage, sector, country and collateral coverage.
3. **Dimensional concentration.** Industry, geography, product, collateral type and counterparty, each with share, HHI, band and limit position, per `BR-CRR-005`.
4. **Combination concentration.** The six named dimension pairs.
5. **Limit position.** Every credit limit with utilisation, warning and breach status per `BR-CRR-011`, separating FX-driven from exposure-driven movement.
6. **Data quality panel.** Size of the `UNCLASSIFIED` bucket per dimension, and any disagreement between the stored `large_exposure_flag` and the calculated result.

**Measures.** `MET-017`, `MET-018`, `MET-019`, plus EAD, net exposure and current exposure per `BR-CRR-002`, each labelled with which measure it is.

**Rules.** `BR-CRR-001` to `BR-CRR-006`, `BR-CRR-011`, `BR-DQ-011`.

**Required behaviours.**
- Every exposure figure states its measure. A concentration report that does not say whether it is EAD or net exposure is unusable.
- Double-counted exposure arising from joint control under `BR-CRR-003` is disclosed as a reconciling line, never hidden.
- The report must be producible for an arbitrary `as_of_date` within four hours, which is programme objective O3 and is tested as such.

**Test.** `AC-204`.

---

## RPT-004 — Impairment Pack

| Field | Value |
|---|---|
| Owner | P-02, jointly with P-06 for the ledger sections |
| Consumers | P-01, P-03, P-05, P-13, P-14, external audit |
| Grain | One row per portfolio segment per stage per legal entity per reporting date |
| Cadence | Monthly, with an extended quarterly pack |
| Latency SLO | T+3 business days from month end |
| Entitlement | `ENT-2` |
| Retention | 10 years |

**Sections.**
1. **Provision position.** Gross carrying amount, provision, coverage ratio, by stage and segment. IFRS 9 and CECL side by side per `BR-IMP-001`, with the bridge between them reconciling exactly.
2. **Stage distribution.** Balance and count by stage, with the proportion of stage 2 driven solely by the 30-day backstop, per `BR-IMP-002`.
3. **Movement attribution.** The full ten-line decomposition of `BR-IMP-009`, with a residual line that must read zero.
4. **Model output versus final.** Model ECL, post-model adjustment, overlay and final provision shown separately per `BR-IMP-008`, with each overlay's rationale, approver, expiry and age in quarters.
5. **Scenario sensitivity.** ECL under each macroeconomic scenario at 100 % weight, and the weighted result, with the weights shown.
6. **Overrides.** Every stage override under `BR-IMP-011` with proposer, approver, reason, ECL impact and expiry. Aggregate override percentage against the 3 % cap.
7. **Risk to finance reconciliation.** Per `BR-IMP-010`, at legal entity, segment and GL account grain.
8. **Write-offs and recoveries.** Per `BR-IMP-012`, shown separately, never netted.

**Measures.** `MET-008`, `MET-009`, `MET-010`, `MET-011`, `MET-012`, `MET-013`, `MET-014`.

**Rules.** All of `BR-IMP-001` to `BR-IMP-012`, plus `BR-CRR-010` and `BR-IMP-007`.

**Quality gate.** Does not publish if the `BR-IMP-009` residual is non-zero, if the risk-to-finance reconciliation has an open material difference, or if any unapproved overlay is present.

**Notes.** This is the pack external audit will test. Every number on it must have a drill path to the individual exposures behind it, and that drill must respect entitlement.

**Test.** `AC-205`.

---

## RPT-005 — Stage Migration and SICR Attribution

| Field | Value |
|---|---|
| Owner | P-02, produced by P-03 |
| Consumers | P-01, P-06, P-13, external audit |
| Grain | One row per exposure that changed stage between two reporting dates |
| Cadence | Monthly |
| Latency SLO | T+3 business days |
| Entitlement | `ENT-2` |
| Retention | 10 years |

**Content.** For every migrating exposure: counterparty, facility, segment, prior stage, new stage, migration date, the specific SICR trigger that fired, PD at origination, PD at prior date, PD now, relative and absolute PD movement against the segment thresholds, days past due, forbearance flag, watchlist status, covenant status, ECL before, ECL after and ECL impact.

**Required panels.**
- **Trigger distribution.** Count and balance by trigger type, so that the split between quantitative, qualitative and backstop is visible at a glance.
- **Backstop concentration.** The proportion of stage 2 entering on the 30-day backstop alone. P-02 asks this question every month and the report must answer it without being reconfigured.
- **Missing origination PD.** Exposures that could not be quantitatively tested because origination PD is unavailable, per `BR-IMP-002`. This is a data quality exposure and is sized in both count and balance.
- **Rebuttals.** Backstop rebuttals with evidence and approver, and the rebuttal rate against the 5 % cap.
- **Rating currency.** Exposures whose rating is stale under `BR-CRR-007`, and those beyond 18 months forcing standardised treatment.

**Measures.** `MET-010`, `MET-008`, `MET-015`.

**Rules.** `BR-IMP-002`, `BR-IMP-003`, `BR-IMP-011`, `BR-CRR-007`, `BR-CRR-008`.

**Test.** `AC-206`.

---

## RPT-006 — Watchlist and Early Warning

| Field | Value |
|---|---|
| Owner | P-03 |
| Consumers | P-02, P-11 for their own portfolio only |
| Grain | One row per counterparty on, or triggering entry to, the watchlist |
| Cadence | Daily |
| Latency SLO | T+1 business day, by 08:00 |
| Entitlement | `ENT-2` for risk, `ENT-4` scoped to assignment for P-11 |
| Retention | 7 years |

**Content.** Every counterparty with any `BR-CRR-009` trigger active, showing **all** triggers on one row, not one row per trigger. This is the explicit design response to P-02's failure mode.

Columns: counterparty, connected group, total EAD, rating and rating direction, IFRS 9 stage, maximum days past due across facilities, covenant status and nearest test date, collateral coverage ratio and consecutive days below 100 %, forbearance flag, external rating and outlook, market signal where observable, watchlist entry date, days on watchlist, owning analyst, owning relationship manager, next review date.

**Required behaviours.**
- New entries since the prior run are visually distinct.
- Counterparties that meet an exit condition are flagged for decision but never auto-exit, per `BR-CRR-009`.
- A trigger caused by a data quality failure is labelled as such, so that analysts do not spend time on an artefact. The label does not suppress the trigger.
- Where P-11 consumes this report, anti-money-laundering status is entirely absent, per `BR-AML-008`. Not masked, absent.

**Rules.** `BR-CRR-009`, `BR-CRR-007`, `BR-CRR-010`, `BR-CRR-013`, `BR-AML-008`.

**Test.** `AC-207`.

---

## RPT-007 — Covenant Compliance and Waiver Register

| Field | Value |
|---|---|
| Owner | P-03 |
| Consumers | P-02, P-11 scoped, P-14 |
| Grain | One row per covenant per test date |
| Cadence | Daily |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-2`, `ENT-4` scoped for P-11 |
| Retention | 7 years |

**Sections.**
1. **Breaches.** Effective breaches per `BR-CRR-013`, with facility, obligor, covenant, threshold, actual, breach date, grace period status, cure mechanism and consequence.
2. **Reporting breaches.** Covenants that could not be tested because financial information was not delivered, aged from the reporting deadline. Distinct from financial breaches, always.
3. **Near breaches.** Every covenant within 10 % of its threshold, which is the panel that creates value.
4. **Waivers.** Active waivers with effective and expiry dates, and waivers expiring within 30 days, because expiry reinstates the breach automatically.
5. **Cross-default propagation.** Breaches propagated under `cross_default_flag`, with their origin identified.
6. **Upcoming tests.** Every covenant with a test date in the next 90 days, which is the panel P-11 uses.

**Measures.** `MET-021`.

**Rules.** `BR-CRR-013`, `BR-CRR-009`.

**Test.** `AC-208`.

---

## RPT-008 — Origination Pipeline and Underwriting Quality

| Field | Value |
|---|---|
| Owner | P-02 |
| Consumers | P-10, P-11, P-01 |
| Grain | One row per credit application, aggregated to vintage cohort for the performance sections |
| Cadence | Weekly for pipeline, monthly for vintage performance |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-2`, `ENT-4` scoped for P-11 |
| Retention | 7 years |

**Sections.**
1. **Pipeline.** Applications by stage, value, age in stage, and stage conversion rates.
2. **Decision outcomes.** Approval, decline and withdrawal rates by channel, segment and product, with decline reason distribution.
3. **Approval leakage.** Approved but undrawn, aged, per `BR-CRR-014`.
4. **Vintage performance.** By origination quarter at 6, 12, 24 and 36 months: 90+ delinquency, stage 2 migration, charge-off, average rating migration.
5. **Policy exceptions.** Exception lending isolated from policy-compliant lending in every vintage cut.
6. **Compliance gate.** Any application progressed with `kyc_completed` false or `aml_screening_status` uncleared, which is a blocking failure per `BR-CRR-014`.

**Rules.** `BR-CRR-014`, `BR-AML-002`.

**Test.** `AC-209`.

---

## RPT-018 — Counterparty Credit Exposure and Valuation Adjustments

| Field | Value |
|---|---|
| Owner | P-02 |
| Consumers | P-01, P-03, P-04 |
| Grain | One row per netting set per counterparty per measurement date |
| Cadence | Daily |
| Latency SLO | T+1 business day by 09:00 |
| Entitlement | `ENT-2` |
| Retention | 7 years |

**Content.** Current exposure, potential future exposure, expected exposure, net exposure, collateral value, EAD, CVA, DVA, FVA, CVA capital charge, CVA approach, wrong-way risk flag, netting agreement reference and enforceability evidence.

**Required behaviours.**
- CVA is presented gross. Netting it against DVA is prohibited per `BR-MKT-003`.
- Netting benefit is shown as an explicit line, with the master agreement that supports it. Netting without evidence is a blocking failure.
- Wrong-way risk exposures are a separate panel, not a flag buried in a wide table.

**Rules.** `BR-MKT-003`, `BR-CRR-002`, `BR-COL-003`.

**Test.** `AC-210`.

---

## RPT-019 — Collateral and Margin Call Ageing

| Field | Value |
|---|---|
| Owner | P-02 |
| Consumers | P-03, P-04, collateral operations |
| Grain | One row per margin call, plus a collateral inventory section at asset grain |
| Cadence | Intraday, refreshed every 30 minutes during market hours |
| Latency SLO | 30 minutes |
| Entitlement | `ENT-2` |
| Retention | 7 years |

**Sections.**
1. **Open calls.** Issued, agreed, disputed and unmet, aged from issue, with amount, counterparty, agreement and cure deadline.
2. **Unmet beyond cure.** Escalated as credit events per `BR-COL-002`, feeding `RPT-006`.
3. **Disputes.** Tracked separately from unmet, with dispute age and disputed amount.
4. **Collateral inventory.** By asset class, issuer, currency and eligibility, with valuation date, staleness status and applied haircut.
5. **Stale valuations.** Assets beyond their maximum valuation age under `BR-IMP-007`, with the resulting valuation treatment shown.
6. **Wrong-way collateral.** Collateral issued by the obligor or its connected group, which is ineligible per `BR-COL-003`.
7. **Concentration.** Collateral concentration by issuer, asset class and currency against limits.

**Rules.** `BR-COL-001`, `BR-COL-002`, `BR-COL-003`, `BR-IMP-007`.

**Test.** `AC-211`.

---

## RPT-017 — Market Risk and Limit Utilisation

| Field | Value |
|---|---|
| Owner | P-01, produced by Market Risk |
| Consumers | P-04, P-13, P-14 |
| Grain | One row per trading book per limit per business date |
| Cadence | Daily |
| Latency SLO | T+1 business day by 08:00 |
| Entitlement | `ENT-2` |
| Retention | 7 years |

**Content.** VaR at the limit's own confidence level and holding period, stressed VaR, limit, utilisation percentage, warning and breach status, profit and loss, backtesting exception count over 250 days and current zone.

**Required behaviours.**
- Any conversion between confidence levels or holding periods is shown with its method, per `BR-MKT-001`.
- Book hierarchy for utilisation matches the limit's own scope. Cross-level comparison is a defect.
- Backtesting exceptions include the clean-P&L basis statement, per `BR-MKT-002`.

**Rules.** `BR-MKT-001`, `BR-MKT-002`, `BR-CRR-011`.

**Test.** `AC-212`.

---

# Part C — Treasury and capital reporting (P-04)

## RPT-012 — Daily Liquidity and Intraday Position

| Field | Value |
|---|---|
| Owner | P-04 |
| Consumers | P-01, P-05, P-06, ALCO |
| Grain | One row per legal entity per currency per consolidation level per business date |
| Cadence | Daily, every business day without exception |
| Latency SLO | **Available by 09:00 local on T+1.** This is the hardest latency requirement in the specification |
| Entitlement | `ENT-5` |
| Retention | 10 years |

**Sections.**
1. **Headline.** Group LCR and NSFR at each consolidation level, against minima, with headroom in ratio points and in absolute currency.
2. **Binding constraint.** The entity, currency and consolidation combination with the least headroom, per `BR-LIQ-003`, with an explicit statement of whether surplus elsewhere can be transferred to it.
3. **HQLA composition.** Level 1, 2A and 2B before and after caps and haircuts, with the cap effect shown, plus encumbered and unencumbered split and the overnight change in encumbrance.
4. **Outflow composition.** Retail deposit, wholesale funding, secured funding, derivative and committed facility outflows, with the largest movers against the prior day.
5. **Inflow position.** Contractual inflows before and after the 75 % cap.
6. **Intraday.** Peak usage, available liquidity at peak, time of peak, and throughput against the value-weighted settlement profile, per `BR-LIQ-004`.
7. **Early warning indicators.** Every liquidity KRI with its status.
8. **Quality.** The `data_quality_score` of every consumed dataset and the explicit qualification where any is below threshold.

**Measures.** `MET-005`, `MET-006`, `MET-007`.

**Rules.** `BR-LIQ-001` to `BR-LIQ-004`, `BR-DQ-008`, `BR-DQ-012`.

**Quality gate.** **Publishes at 09:00 regardless of completeness.** Where a feed is missing, the report publishes with the gap named, the affected population quantified and the ratio marked as qualified. It is recomputed and reissued on arrival. Delaying the 09:00 delivery is a worse failure than publishing a qualified number, per `BR-DQ-012`.

**Notes.** An end-of-day intraday measure that hides a peak within 5 % of available liquidity is a false assurance and fails `BR-LIQ-004` even when every number on it is arithmetically correct.

**Test.** `AC-221`.

---

## RPT-013 — NSFR and Funding Plan

| Field | Value |
|---|---|
| Owner | P-04 |
| Consumers | P-01, P-05, P-06, ALCO |
| Grain | One row per ASF or RSF category per legal entity per consolidation level per month end |
| Cadence | Monthly |
| Latency SLO | T+5 business days |
| Entitlement | `ENT-5` |
| Retention | 10 years |

**Content.** ASF and RSF by category and residual maturity bucket, with factors applied; NSFR by entity and consolidation level; movement from prior month attributed to new funding, maturity roll-down across bucket boundaries, balance sheet growth and behavioural reclassification.

**Required behaviour.** Roll-down effects, where the ratio changes because time passed rather than because anything was transacted, are shown as a separate attribution line. This is the line that prevents an unnecessary funding decision.

**Measures.** `MET-006`.

**Rules.** `BR-LIQ-002`, `BR-LIQ-005`.

**Test.** `AC-222`.

---

## RPT-014 — ALCO Pack

| Field | Value |
|---|---|
| Owner | P-04 |
| Consumers | ALCO, P-01, P-06, P-14 |
| Grain | Mixed; each section states its own grain |
| Cadence | Monthly |
| Latency SLO | T+6 business days, three business days before the ALCO meeting |
| Entitlement | `ENT-5` |
| Retention | 10 years |

**Sections.** Balance sheet position and mix; interest rate risk in the banking book with economic value and earnings sensitivity across the mandated rate shocks; liquidity position and survival horizon under each stress scenario; funding plan against actual issuance; capital position and forecast; FTP curve and any proposed change; ALCO resolutions outstanding from prior meetings with owner and due date.

**Measures.** `MET-001`, `MET-004`, `MET-005`, `MET-006`, `MET-024`, `MET-025`.

**Rules.** `BR-LIQ-005`, `BR-LIQ-006`, `BR-CAP-001`, `BR-CAP-002`.

**Test.** `AC-223`.

---

## RPT-015 — FTP and Contribution Margin by Line of Business

| Field | Value |
|---|---|
| Owner | P-04, jointly with P-06 |
| Consumers | P-01, P-06, P-10, P-11, business heads |
| Grain | One row per product per line of business per legal entity per month |
| Cadence | Monthly |
| Latency SLO | T+6 business days |
| Entitlement | `ENT-5` for full detail, `ENT-4` scoped for business heads |
| Retention | 7 years |

**Content.** Customer rate, FTP rate with its five components shown separately, net interest margin, contribution margin, allocated cost, allocated capital, RAROC, and the treasury residual.

**Required behaviours.**
- The five FTP components are always shown separately, because every FTP dispute with a business starts by disagreeing with one component, per `BR-LIQ-006`.
- The allocation must sum to zero across all lines of business plus treasury residual. The report displays the sum, and a non-zero sum is a blocking failure.
- Products where contribution margin is negative after FTP and capital are highlighted, since that is the entire commercial purpose of the report.

**Measures.** `MET-023`, `MET-024`, `MET-025`.

**Rules.** `BR-LIQ-006`, `BR-CAP-008`, `BR-FIN-006`.

**Test.** `AC-224`.

---

# Part D — Regulatory reporting (P-05)

## RPT-009 — Regulatory Capital Reconciliation

| Field | Value |
|---|---|
| Owner | P-05 |
| Consumers | P-04, P-06, P-01, P-14, external audit |
| Grain | One row per regulatory line item per return per legal entity per reporting date |
| Cadence | Quarterly, aligned to each return's deadline |
| Latency SLO | Return deadline minus 4 business days |
| Entitlement | `ENT-5` |
| Retention | 10 years, frozen per `BR-REG-004` |

**Sections.**
1. **Return position.** Each capital return's line items with their submitted values.
2. **Ledger bridge.** Every line reconciled to the general ledger, with each reconciling item named, quantified and owned, per `BR-REG-003`.
3. **Risk system bridge.** Credit RWA on the return reconciled to the sum of `risk.credit_exposure` RWA, per `BR-DQ-004` reconciliation 4.
4. **Validation results.** Every supervisory validation rule, its result, and for each failure the correction or the recorded explanation and approver, per `BR-REG-002`.
5. **Period-on-period movement.** Each line's movement attributed to business change, methodology change, model change and restatement.
6. **As-reported comparison.** The prior submission as filed against what the same query returns today, with every difference classified under `BR-DQ-009`. This is P-05's defining requirement.
7. **Approach and floor.** Standardised parallel run against internal model result, with the output floor position per `BR-CAP-004`.

**Measures.** `MET-001` to `MET-004`.

**Rules.** `BR-CAP-001` to `BR-CAP-005`, `BR-REG-002`, `BR-REG-003`, `BR-REG-004`, `BR-DQ-004`, `BR-DQ-009`.

**Quality gate.** Does not publish, and no submission proceeds, while any validation rule failure is neither corrected nor explained with a recorded approver.

**Test.** `AC-231`.

---

## RPT-010 — FR Y-14 Loan-Level Submission Extract

| Field | Value |
|---|---|
| Owner | P-05 |
| Consumers | P-02, P-06, P-14 |
| Grain | One row per loan or facility per schedule per reporting date, per the schedule's own definition |
| Cadence | Quarterly for Y-14Q, monthly for Y-14M |
| Latency SLO | Deadline minus 5 business days |
| Entitlement | `ENT-5`. Party identifiers visible where the schedule requires them, masked elsewhere |
| Retention | 10 years, frozen |

**Content.** The full attribute set required by each schedule, sourced from the certified layer, never from a report-level derivation.

**Required behaviours.**
- Any schedule attribute with no corresponding `banking_ecm` column is a gap raised against the data model. It is never filled by an extract-level calculation, per `BR-REG-006`.
- Population reconciles to the FR Y-9C balance sheet, with reconciling items named.
- Population movement from the prior submission is explained: new, matured, repaid, transferred, threshold entry, threshold exit.

**Rules.** `BR-REG-001`, `BR-REG-004`, `BR-REG-006`, `BR-CRR-001`, `BR-CRR-010`, `BR-IMP-003`.

**Test.** `AC-232`.

---

## RPT-011 — AnaCredit Submission and Population Control

| Field | Value |
|---|---|
| Owner | P-05 |
| Consumers | P-02, P-12, P-14 |
| Grain | One row per instrument per reporting month, plus counterparty, protection and accounting datasets at their own grains |
| Cadence | Monthly |
| Latency SLO | Deadline minus 5 business days |
| Entitlement | `ENT-5` |
| Retention | 10 years, frozen |

**Sections.** Instrument dataset; counterparty reference dataset including protection providers who are not OAFG customers; protection received dataset; accounting dataset; population movement analysis; counterparty reference completeness, which is the most common failure point and is tested explicitly per `BR-REG-005`.

**Rules.** `BR-REG-001`, `BR-REG-004`, `BR-REG-005`, `BR-DQ-002`, `BR-DQ-006`.

**Quality gate.** Does not submit while any counterparty in the population has incomplete reference data.

**Test.** `AC-233`.

---

# Part E — Finance reporting (P-06)

## RPT-028 — Financial Close Control Tower

| Field | Value |
|---|---|
| Owner | P-06 |
| Consumers | P-04, P-05, P-14, all close task owners |
| Grain | One row per close task per accounting period per legal entity |
| Cadence | Continuous during the close window, refreshed hourly at minimum and on every status change |
| Latency SLO | 15 minutes from a status change |
| Entitlement | `ENT-5` |
| Retention | 7 years |

**Sections.**
1. **Critical path.** The computed critical path to sign-off, recomputed on every status change per `BR-FIN-004`, with time to sign-off and the current bottleneck task.
2. **Task status.** Every task with owner, due time, predecessors, status and lateness, with late-on-path tasks distinguished from late-off-path.
3. **Open reconciliations.** Subledger to GL differences by entity and control account, with materiality position per `MAT-03`.
4. **Manual journals.** Late-period manual journals above threshold, individually, with preparer, approver and value, per `BR-FIN-002`.
5. **Intercompany.** Residual after elimination, by pair, per `BR-FIN-005`.
6. **Provision posting.** Risk provision rows without a `journal_entry_id`, which block sign-off per `BR-IMP-010`.
7. **Control exceptions.** Self-approved journals, unbalanced entries, sign-offs attempted with open material differences.

**Measures.** `MET-039`, `MET-040`, `MET-041`.

**Rules.** `BR-FIN-001` to `BR-FIN-005`, `BR-IMP-010`.

**Notes.** The value of this report is entirely in moving discovery earlier. A daily refresh would not meet its purpose, which is why the cadence is hourly and event-driven.

**Test.** `AC-241`.

---

## RPT-029 — Reconciliation and Control Attestation

| Field | Value |
|---|---|
| Owner | P-06 |
| Consumers | P-05, P-14, external audit |
| Grain | One row per reconciliation per control account per legal entity per period |
| Cadence | Monthly |
| Latency SLO | T+7 business days |
| Entitlement | `ENT-5`, `ENT-6` for audit |
| Retention | 10 years |

**Content.** Every reconciliation in the `BR-DQ-004` set plus every subledger-to-GL reconciliation, with balance A, balance B, difference, materiality position, ageing of the difference, owner, explanation and attestation status.

**Required behaviours.**
- Differences below materiality still carry an owner and an age, per `MAT-04`.
- Attestation records who attested, when, and on what evidence. An attestation without evidence is a control failure.
- SOX control operation is evidenced per control, not asserted in aggregate.

**Measures.** `MET-040`.

**Rules.** `BR-FIN-003`, `BR-DQ-004`, `BR-DQ-010`, `BR-AUD-002`.

**Test.** `AC-242`.

---

## RPT-030 — Segment Performance

| Field | Value |
|---|---|
| Owner | P-06 |
| Consumers | P-01, P-04, P-10, P-11, business heads, Board |
| Grain | One row per segment per legal entity per month |
| Cadence | Monthly |
| Latency SLO | T+7 business days |
| Entitlement | `ENT-5` full, `ENT-4` scoped for business heads |
| Retention | 10 years |

**Content.** Revenue, FTP, direct cost, allocated cost, cost of risk, profit before tax, allocated capital, return on allocated capital, RAROC, cost-to-income ratio, and the reconciliation of segments plus unallocated to the group total.

**Required behaviours.**
- Segments plus unallocated must equal group exactly. The report shows the check.
- Unallocated above 5 % of group cost is flagged as an allocation quality issue per `BR-FIN-006`.
- Allocation basis changes trigger prior-period restatement on the new basis, with both bases shown in the transition period.

**Measures.** `MET-013`, `MET-023`, `MET-024`, `MET-025`.

**Rules.** `BR-FIN-006`, `BR-CAP-008`, `BR-LIQ-006`.

**Test.** `AC-243`.

---

## RPT-026 — Payment Operations and Straight-Through Processing

| Field | Value |
|---|---|
| Owner | P-06, produced by Payments Operations |
| Consumers | P-04, P-09, P-10 |
| Grain | One row per payment type per channel per currency per corridor per hour |
| Cadence | Intraday, hourly |
| Latency SLO | 60 minutes |
| Entitlement | `ENT-4` |
| Retention | 3 years detailed, 7 years aggregated |

**Content.** Volume, value, STP rate, manual repair rate, automated repair rate, exception count and value, rejection and return rates by reason, average and 95th percentile processing time, and cut-off adherence.

**Required behaviours.**
- STP is reported by type, channel, currency and corridor. A single group STP figure is not actionable and does not satisfy this specification.
- Exceptions are prioritised by time to cut-off, not by age, per `BR-PAY-002`.
- Repeated exceptions on the same beneficiary or corridor are surfaced as a static-data problem and routed to `RPT-038`, not to payments operations.
- Any payment released with pending sanctions screening appears as a blocking control failure, per `BR-PAY-003`.

**Measures.** `MET-035`, `MET-036`.

**Rules.** `BR-PAY-001`, `BR-PAY-002`, `BR-PAY-003`.

**Test.** `AC-244`.

---

## RPT-027 — Nostro Reconciliation Breaks

| Field | Value |
|---|---|
| Owner | P-04, jointly with P-06 |
| Consumers | P-05, P-14 |
| Grain | One row per unmatched item per nostro account |
| Cadence | Daily |
| Latency SLO | T+1 business day by 10:00 |
| Entitlement | `ENT-5` |
| Retention | 7 years |

**Content.** Break amount, currency, value date, age from value date, account, correspondent, direction, suspected cause, owner and status. Ageing buckets of 0–1, 2–5, 6–30 and over 30 days, with everything over 30 days escalated to P-06 and raised as a potential operational loss event under `BR-ORX-001`.

**Measures.** `MET-038`.

**Rules.** `BR-LIQ-007`, `BR-ORX-001`.

**Test.** `AC-245`.

---

# Part F — Financial crime and fraud reporting (P-07, P-08, P-09)

## RPT-021 — Regulatory Filing Deadline Countdown

| Field | Value |
|---|---|
| Owner | P-07 |
| Consumers | P-08, P-14, Board Financial Crime Committee |
| Grain | One row per filing obligation |
| Cadence | Refreshed every 4 hours, every day including non-business days |
| Latency SLO | 4 hours |
| Entitlement | `ENT-3` only. `ENT-6` for audit under mandate |
| Retention | 10 years |

**Design principle.** This is a countdown, not a status list. It is ordered by time remaining, ascending. The most urgent obligation is always the first row on the screen.

**Content.** Filing type, subject reference, jurisdiction, detection date, statutory deadline, hours remaining or overdue, current status, assigned owner, blocking reason where blocked, and escalation state.

**Sections.**
1. **Overdue.** Any filing past its statutory deadline. This section is red and is never empty by design tolerance; it should be empty in practice, and its being non-empty is a reportable regulatory incident.
2. **Due within 72 hours.**
3. **Due within 7 days.**
4. **Continuing activity due.** Filings required under the 120-day continuing activity rule, per `BR-AML-007`.
5. **Regulatory commitments.** Open lookbacks under `BR-AML-010`, consent order obligations, exam finding remediation, each with its deadline.

**Required behaviours.**
- The clock runs from `detection_date`, never from the escalation or investigation date, per `BR-AML-007`. The platform must make it impossible to represent a later start.
- Deadlines falling on non-business days do not extend, so the report runs on non-business days.
- Every figure on this report is subject to `BR-AML-008`. It is visible to `ENT-3` alone.

**Measures.** `MET-029`.

**Rules.** `BR-AML-007`, `BR-AML-008`, `BR-AML-010`.

**Test.** `AC-251`.

---

## RPT-022 — KYC Review Backlog and High-Risk Population

| Field | Value |
|---|---|
| Owner | P-07 |
| Consumers | P-08, P-11 for their own clients only, P-14 |
| Grain | One row per party per review cycle |
| Cadence | Daily |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-3`. P-11 sees only their assigned clients and only the fact that a review is due, never the risk rating or its drivers |
| Retention | 10 years |

**Sections.**
1. **Overdue reviews.** By risk rating and ageing band, with the transacting versus dormant split, per `BR-AML-002`.
2. **High-risk overdue.** The regulatory exposure. Any high-risk review overdue beyond 90 days carries a transaction restriction recommendation to P-07.
3. **Due in 30, 60 and 90 days.** The forward workload, which is what prevents the backlog.
4. **Incomplete documentation.** Reviews where `documentation_completeness_flag` is false, with `outstanding_document_list`.
5. **Verification gaps.** Source of funds, source of wealth and beneficial ownership not verified, per `BR-AML-003`.
6. **Rating changes.** Parties whose rating changed this period, with the trigger, per `BR-AML-001`.
7. **Beneficial ownership chains.** Chains not resolving to a natural person, which is a qualifying failure.

**Measures.** `MET-030`.

**Rules.** `BR-AML-001`, `BR-AML-002`, `BR-AML-003`.

**Notes.** P-11's view of this report is deliberately impoverished. They need to know a review is due because it blocks their client's drawdown. They must not learn why the client is high risk.

**Test.** `AC-252`.

---

## RPT-023 — Sanctions Screening Effectiveness

| Field | Value |
|---|---|
| Owner | P-07 |
| Consumers | P-08, P-14 |
| Grain | One row per screening event, aggregated by list and algorithm for the effectiveness sections |
| Cadence | Weekly, with a daily true-match panel |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-3` |
| Retention | 10 years |

**Content.** Screening volume by trigger type, hit volume, true match volume, false positive rate by list and by matching algorithm, average and 95th percentile time to disposition, list version currency, and any activity released while screening was pending.

**Required behaviours.**
- A false positive rate above 98 % on any list is flagged as an effectiveness concern, because at that rate analysts stop reading, per `BR-AML-004`.
- List version in force at screening time is recorded and shown. Retrospective screening against a newer list is a separate exercise with its own section.
- Any payment released on pending screening is a blocking control failure and appears at the top of the report, per `BR-PAY-003`.

**Measures.** `MET-031`.

**Rules.** `BR-AML-004`, `BR-PAY-003`.

**Test.** `AC-253`.

---

## RPT-020 — AML Alert and Case Operations

| Field | Value |
|---|---|
| Owner | P-08 |
| Consumers | P-07, P-14 |
| Grain | One row per alert, plus a case-level section at case grain |
| Cadence | Refreshed every 15 minutes |
| Latency SLO | 15 minutes |
| Entitlement | `ENT-3`, scoped to assigned queue for investigators |
| Retention | 10 years |

**Sections.**
1. **SLA position.** Alerts breaching SLA now, and alerts breaching within 24 hours, per the `BR-AML-005` matrix. Forward view first.
2. **Queue.** Open alerts by priority, type, age, assigned analyst and status.
3. **Subject context.** For any selected subject: every account, every related party from `BR-CRR-003` hierarchy traversal, every payment counterparty, every prior alert and case, every fraud alert on the same subject, KYC status, risk rating and its drivers. This one panel is the reason the platform is built on a single model.
4. **Productivity.** Alerts dispositioned per analyst, average handling time, quality sample results.
5. **Conversion.** Alert-to-case conversion by rule and by type, per `BR-AML-006`.
6. **Ageing cases.** Cases by age band with the filing deadline position from `RPT-021`.
7. **Duplicates.** Alerts on subjects with an existing open case, which should have merged.

**Measures.** `MET-028`, `MET-029`.

**Rules.** `BR-AML-005`, `BR-AML-006`, `BR-AML-008`, `BR-CRR-003`.

**Notes.** The subject context panel must load in under 5 seconds, per `NFR-006`. An investigator who waits 30 seconds for context will stop asking for it, and the platform's whole value proposition for P-08 disappears.

**Test.** `AC-254`.

---

## RPT-024 — Fraud Loss and Detection Performance

| Field | Value |
|---|---|
| Owner | P-09 |
| Consumers | P-07, P-10, P-01, P-14 |
| Grain | One row per alert for the operational sections; one row per channel per typology per day for the loss sections |
| Cadence | Refreshed every 5 minutes for operational panels, daily for performance |
| Latency SLO | 5 minutes for alerts and losses |
| Entitlement | `ENT-3` |
| Retention | 7 years |

**Sections.**
1. **Today against appetite.** Gross loss, recovery and net loss today by channel and typology, against the daily appetite threshold.
2. **Alert queue.** Open alerts by severity, score, age and assignee.
3. **Loss trend.** Net loss rate in basis points of throughput, by channel and typology, over 13 periods.
4. **Recovery.** Recovery rate and open recoveries by age, per `BR-FRD-001`.
5. **Network clusters.** Emerging clusters by shared device, address, beneficiary or merchant, with linkage strength, per `BR-FRD-003`.
6. **Chargebacks.** Volume, value, stage deadlines and merchant chargeback ratios against network thresholds, per `BR-FRD-004`.
7. **Customer impact.** False positive volume and the friction it caused, because detection that blocks legitimate customers has a cost that must be visible next to the benefit.

**Measures.** `MET-032`, `MET-033`, `MET-034`.

**Rules.** `BR-FRD-001`, `BR-FRD-003`, `BR-FRD-004`, `BR-ORX-001`.

**Notes.** Gross loss, recovery and net loss are never conflated, and loss is recognised in the period of the event while recovery is recognised when received, per `BR-FRD-001`.

**Test.** `AC-255`.

---

## RPT-025 — Detection Rule Performance and Tuning

| Field | Value |
|---|---|
| Owner | P-09 |
| Consumers | P-07, P-13, P-14 |
| Grain | One row per detection rule per rule version per period |
| Cadence | Weekly |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-3` |
| Retention | 7 years |

**Content.** Alert volume, precision, value detected, value missed, average score distribution, threshold, and the rule's version and deployment date.

**Required behaviours.**
- Performance is never compared across a rule version change without the change being marked. A trend line spanning a version change with no marker is prohibited, per `BR-FRD-002`.
- Rules with no true positives in six months appear with both the "no true positives" fact and the typology coverage they provide, so P-09 can distinguish a noisy rule from a rare-typology rule.
- Detection rules are models under `BR-MDL-001`, so this report feeds `RPT-034`.

**Measures.** `MET-033`.

**Rules.** `BR-FRD-002`, `BR-MDL-001`, `BR-MDL-003`.

**Test.** `AC-256`.

---

# Part G — Customer and channel reporting (P-10, P-11)

## RPT-031 — Client Relationship View

| Field | Value |
|---|---|
| Owner | P-11 |
| Consumers | P-03, P-02 |
| Grain | One row per client group, with linked detail at facility, account and interaction grain |
| Cadence | Daily, with intraday refresh of risk-relevant changes |
| Latency SLO | T+1 business day, same-day for rating, limit and covenant changes on the assigned portfolio |
| Entitlement | `ENT-4`, restricted by `channel.rm_client_assignment` and `account.rm_account_assignment` per `BR-CUS-002` |
| Retention | 3 years |

**Sections.**
1. **Group structure.** The connected client group from `BR-CRR-003`, with each entity's role and jurisdiction.
2. **Exposure.** Facilities, drawn, undrawn, committed, maturities, pricing, all-in rate.
3. **Collateral.** Assets, valuations, valuation age, coverage ratio.
4. **Covenants.** Status and next test date, from `RPT-007`.
5. **Payments and deposits.** Balances, flows, concentration of counterparties.
6. **Service.** Open interactions, complaints, SLA breaches, onboarding items outstanding.
7. **Profitability.** Revenue, FTP-adjusted contribution margin, allocated capital, return on capital, per `MET-023` and `MET-025`.
8. **Forward calendar.** Covenant tests, maturities, reviews and KYC renewals in the next 90 days.
9. **Recent changes.** Anything that changed on this client in the last 7 days.

**Prohibited content.** Anti-money-laundering alerts, cases, SAR existence, SAR consideration, and any field from which those can be inferred. Absent, not masked, per `BR-AML-008` and `CTL-011`. Where a KYC review is overdue, the RM sees only that a review is due and that it may block drawdown.

**Measures.** `MET-023`, `MET-025`, `MET-042`, `MET-043`.

**Rules.** `BR-CRR-003`, `BR-CUS-002`, `BR-AML-008`, `BR-CRR-013`, `BR-IMP-007`.

**Notes.** P-11's failure mode runs in both directions. An RM who asks for new business on the day of an internal downgrade has been failed by the platform. An RM who learns a client is under investigation has been failed worse, and criminally so.

**Test.** `AC-261`.

---

## RPT-032 — Channel Experience and Service Level

| Field | Value |
|---|---|
| Owner | P-10 |
| Consumers | P-09, P-06, P-01 |
| Grain | One row per channel per region per one-minute interval for availability; one row per journey step for the journey sections |
| Cadence | Refreshed every 5 minutes |
| Latency SLO | 5 minutes |
| Entitlement | `ENT-4` |
| Retention | 90 days at one-minute grain, 3 years at hourly grain |

**Sections.**
1. **Availability.** Uptime percentage and customer-impacting minutes by channel and region, per `BR-CHN-001`. Partial degradation counts as unavailability.
2. **Response time.** Actual against target, at median and 95th percentile.
3. **Incidents.** Open channel incidents with impact and duration.
4. **Journeys.** Completion and abandonment by step, with abandonment attributed to the step where it occurred, per `BR-CHN-002`.
5. **Onboarding.** End-to-end cycle time with the constraining step identified, and time waiting on the customer shown separately.
6. **Authentication and friction.** Step-up authentication rates and their correlation with abandonment, which is where fraud control and customer experience meet.

**Measures.** `MET-044`, `MET-045`.

**Rules.** `BR-CHN-001`, `BR-CHN-002`.

**Notes.** Customer-impacting minutes weights downtime by the sessions that would have occurred, using the equivalent interval from the prior four weeks. Raw uptime percentage understates a peak-hour outage and is not sufficient on its own.

**Test.** `AC-262`.

---

## RPT-033 — Complaints and Conduct Risk

| Field | Value |
|---|---|
| Owner | P-10 |
| Consumers | P-07, P-14, Board Conduct Committee |
| Grain | One row per complaint, aggregated to theme for the trend sections |
| Cadence | Weekly, with a monthly conduct pack |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-4`, `ENT-3` for the conduct-risk sections |
| Retention | 7 years |

**Content.** Volume normalised by product holdings, theme clustering, upheld rate, redress value, resolution timeliness against regulatory deadlines, root cause, and repeat-complaint rate by customer.

**Required behaviours.**
- Normalised volume is the reportable measure. Raw counts favour small products and hide problems, per `BR-CHN-003`.
- Any theme growing more than 50 % quarter on quarter escalates regardless of absolute volume.
- An upheld complaint is a conduct signal even where redress is immaterial. Materiality of redress is not materiality of signal.

**Measures.** `MET-046`.

**Rules.** `BR-CHN-003`.

**Test.** `AC-263`.

---

# Part H — Governance reporting (P-12, P-13, P-14)

## RPT-038 — Data Quality and Critical Data Element Scorecard

| Field | Value |
|---|---|
| Owner | P-12 |
| Consumers | every persona, because every report displays its extract |
| Grain | One row per quality rule per dataset per run |
| Cadence | Every pipeline cycle, at minimum daily |
| Latency SLO | Within one pipeline cycle of the data it measures |
| Entitlement | `ENT-7`. Rule results are visible to all personas for the datasets they consume |
| Retention | 3 years detailed, 7 years aggregated |

**Sections.**
1. **Blocking failures.** Every failing blocking rule, its dataset, the reports it blocks and the regulatory deadlines at risk. This is the first thing on the page.
2. **CDE scorecard.** All 412 critical data elements with owner, rule set, score and trend, per `BR-DQ-001`.
3. **Referential integrity.** Orphan counts by relationship, with CDE relationships first, per `BR-DQ-002`.
4. **Cross-system agreement.** The ten reconciliations of `BR-DQ-004` with their differences against tolerance.
5. **Completeness.** Null rates against the criticality thresholds of `BR-DQ-006`.
6. **Domain conformance.** Invalid values and failed casts, per `BR-DQ-005`, with the `STRING`-typed numeric columns called out specifically.
7. **Freshness.** Every dataset's age against its contract, per `BR-DQ-008`, and every late arrival with its downstream impact.
8. **Ownership gaps.** CDEs without a steward, which are blocking governance failures.
9. **Duplicate metric implementations.** Detected under `BR-DQ-007`.
10. **Suspected party duplicates.** From `BR-CUS-001`, with confidence scores, never auto-merged.
11. **Static data problems.** Repeated payment exceptions on the same beneficiary or corridor, routed here from `RPT-026`.

**Measures.** `MET-050`.

**Rules.** All of `BR-DQ-001` to `BR-DQ-013`, plus `BR-CUS-001`.

**Test.** `AC-271`.

---

## RPT-039 — Lineage, Certification and BCBS 239 Attestation

| Field | Value |
|---|---|
| Owner | P-12 |
| Consumers | P-01, P-05, P-14, supervisors |
| Grain | One row per certified metric per certification cycle |
| Cadence | Quarterly, with continuous lineage availability |
| Latency SLO | Lineage always current with deployed code; attestation quarterly |
| Entitlement | `ENT-7`, `ENT-6` for audit |
| Retention | 10 years |

**Sections.**
1. **Metric certification register.** Every `MET-nnn` with owner, definition version, last change, approver, model dependencies from `BR-MDL-005` and consuming reports.
2. **Lineage.** For every board-reported and regulatory-submitted figure, the full path from source system to published number, generated from deployed pipeline code, never maintained by hand.
3. **BCBS 239 principle evidence.** Each principle with the artefacts that evidence it and any gaps, stated plainly.
4. **Change history.** Every certified metric change in the period with its change-control record.
5. **Programme objectives.** O1 to O6 from [00](./00-programme-charter-and-scope.md#21-programme-objectives), measured.
6. **Impact analysis.** For any nominated source feed, the reports affected by its failure and which of them carry regulatory deadlines.

**Rules.** `BR-DQ-007`, `BR-DQ-009`, `BR-MDL-005`, `BR-REG-004`.

**Test.** `AC-272`.

---

## RPT-034 — Model Inventory, Validation and Performance

| Field | Value |
|---|---|
| Owner | P-13 |
| Consumers | P-01, P-02, P-04, P-05, P-14 |
| Grain | One row per model per version |
| Cadence | Monthly |
| Latency SLO | T+5 business days |
| Entitlement | `ENT-2` |
| Retention | 10 years |

**Sections.**
1. **Inventory.** Every model in scope of `BR-MDL-001`, including fraud detection rules and AML monitoring rules, with owner, purpose, asset class, approval status and risk rating.
2. **Validation currency.** Last and next validation against the frequency for the model's risk rating, with escalation lead times applied, per `BR-MDL-002`.
3. **Overdue and expiring.** Models past validation, and models due within the escalation lead time, with any documented extension and its expiry.
4. **Performance.** Gini, AUC-ROC, Brier score, backtesting result and population stability, each against its validation baseline rather than the prior period, per `BR-MDL-003`.
5. **Regulatory impact.** Every regulatory or board-reported metric depending on a model with a red rating, an overdue validation or a failed backtest, via `BR-MDL-005`.
6. **Approach fallbacks.** Exposures that fell back from internal model to standardised under `BR-CAP-007`, with the quantified capital impact.
7. **Unapproved use.** Any use outside approval, which is blocking under `BR-MDL-004`.

**Measures.** `MET-047`, `MET-048`.

**Rules.** `BR-MDL-001` to `BR-MDL-005`, `BR-CAP-007`.

**Notes.** Section 5 is the answer to the supervisory question P-13 must never be unable to answer. It is a query, not an exercise.

**Test.** `AC-273`.

---

## RPT-035 — Model Overrides and Backtesting Exceptions

| Field | Value |
|---|---|
| Owner | P-13 |
| Consumers | P-02, P-01, P-14 |
| Grain | One row per override, one row per backtesting exception |
| Cadence | Quarterly, with monthly override monitoring |
| Latency SLO | T+5 business days |
| Entitlement | `ENT-2` |
| Retention | 10 years |

**Content.** Override rate by model, by direction, by analyst and by approver; overrides lacking direction, reason or committee approval, which are invalid under `BR-CRR-008`; upward overrides beyond two notches without CRO approval; stage overrides against the 3 % cap under `BR-IMP-011`; backtesting exceptions with zone position under `BR-MKT-002`.

**Required behaviour.** A sustained override rate above 15 % on any model is escalated as a model performance signal, not an analyst performance signal, per `BR-CRR-008`. The report frames it that way explicitly.

**Measures.** `MET-048`.

**Rules.** `BR-CRR-008`, `BR-IMP-011`, `BR-MKT-002`, `BR-MDL-003`.

**Test.** `AC-274`.

---

## RPT-036 — Audit Findings and Management Actions

| Field | Value |
|---|---|
| Owner | P-14 |
| Consumers | Audit Committee, P-01, P-06, P-07, P-12, all action owners |
| Grain | One row per finding, one row per management action |
| Cadence | Monthly, with a quarterly Audit Committee pack |
| Latency SLO | T+2 business days |
| Entitlement | `ENT-6` |
| Retention | 10 years |

**Sections.**
1. **Past-due actions.** By days overdue, rating and owner. Ordered by overdue, descending.
2. **Findings by rating and age.** Internal and regulatory findings tracked in the same framework but reported separately, per `BR-AUD-001`.
3. **Extensions.** Every due-date extension with approver, and any finding extended three or more times, which goes to the Audit Committee regardless of rating.
4. **Awaiting validation.** Closed by management, not yet validated by audit. Management assertion is not closure.
5. **Repeat findings.** Findings whose root cause recurred, rated at least one level higher.
6. **Root cause themes.** Clustering across business units, which is where systemic weakness shows.
7. **Segregation gaps.** Controls performed and monitored by the same team, per `BR-AUD-002`.

**Measures.** `MET-049`.

**Rules.** `BR-AUD-001`, `BR-AUD-002`.

**Test.** `AC-275`.

---

## RPT-037 — Operational Risk Loss and Key Risk Indicators

| Field | Value |
|---|---|
| Owner | P-14, produced by Operational Risk |
| Consumers | P-01, P-06, P-07, P-09, P-10 |
| Grain | One row per operational risk event; one row per KRI per measurement period |
| Cadence | Monthly |
| Latency SLO | T+5 business days |
| Entitlement | `ENT-2` |
| Retention | 10 years |

**Content.** Gross loss, recoveries, insurance recoveries and net loss by Basel event type and business line; near misses; boundary events flagged to prevent double counting; root cause distribution; corrective action status and overdue actions; every KRI with status, threshold, trend and data quality flag.

**Required behaviours.**
- Event date, discovery date and accounting date are all shown. Trending on the wrong one produces the wrong conclusion, per `BR-ORX-001`.
- A red KRI on flagged data is visually distinguished from a red KRI on clean data, because the response differs, per `BR-ORX-002`.
- Three consecutive periods of deterioration inside the green band is reported as a trend, not ignored because no threshold was breached.

**Measures.** `MET-026`, `MET-027`.

**Rules.** `BR-ORX-001`, `BR-ORX-002`, `BR-FRD-004`, `BR-LIQ-007`.

**Test.** `AC-276`.

---

## RPT-040 — Wealth Portfolio Suitability and Mandate Compliance

| Field | Value |
|---|---|
| Owner | Wealth Chief Operating Officer, reporting to P-10's governance forum |
| Consumers | P-07, P-14, P-02 |
| Grain | One row per managed portfolio per business date |
| Cadence | Daily |
| Latency SLO | T+1 business day |
| Entitlement | `ENT-4`, scoped by `wealth.portfolio_assignment` |
| Retention | 7 years |

**Content.** Portfolio against its investment policy statement and mandate; asset allocation drift against target and tolerance; investment restriction breaches; suitability assessment currency against the client's recorded profile; concentration within the portfolio; performance against benchmark and composite; fee billing accuracy.

**Required behaviours.**
- A restriction breach and an allocation drift are different things with different responses and are never merged into one exception count.
- A suitability assessment past its review date makes every subsequent transaction on that portfolio reportable, which is the point of tracking it daily.
- Portfolios pledged as collateral appear on `RPT-019` as well, and the two views must agree.

**Rules.** `BR-CUS-003`, `BR-COL-003`, `BR-CHN-003`.

**Test.** `AC-277`.

---

## Appendix A — Report to persona matrix

| Report | P-01 | P-02 | P-03 | P-04 | P-05 | P-06 | P-07 | P-08 | P-09 | P-10 | P-11 | P-12 | P-13 | P-14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RPT-001 | **O** | C | | C | | C | C | | | | | | | C |
| RPT-002 | **O** | C | | C | | | C | | C | | | | C | C |
| RPT-003 | C | **O** | C | | C | | | | | | | | | C |
| RPT-004 | C | **O** | C | | C | **O** | | | | | | | C | C |
| RPT-005 | C | **O** | C | | | C | | | | | | | C | |
| RPT-006 | | C | **O** | | | | | | | | C | | | |
| RPT-007 | | C | **O** | | | | | | | | C | | | C |
| RPT-008 | C | **O** | | | | | | | | C | C | | | |
| RPT-009 | C | | | C | **O** | C | | | | | | | | C |
| RPT-010 | | C | | | **O** | C | | | | | | | | C |
| RPT-011 | | C | | | **O** | | | | | | | C | | C |
| RPT-012 | C | | | **O** | C | C | | | | | | | | |
| RPT-013 | C | | | **O** | C | C | | | | | | | | |
| RPT-014 | C | | | **O** | | C | | | | | | | | C |
| RPT-015 | C | | | **O** | | **O** | | | | C | C | | | |
| RPT-016 | **O** | C | | C | C | C | | | | | | | C | C |
| RPT-017 | **O** | | | C | | | | | | | | | C | C |
| RPT-018 | C | **O** | C | C | | | | | | | | | | |
| RPT-019 | | **O** | C | C | | | | | | | | | | |
| RPT-020 | | | | | | | C | **O** | | | | | | C |
| RPT-021 | | | | | | | **O** | C | | | | | | C |
| RPT-022 | | | | | | | **O** | C | | | C | | | C |
| RPT-023 | | | | | | | **O** | C | | | | | | C |
| RPT-024 | C | | | | | | C | | **O** | C | | | | C |
| RPT-025 | | | | | | | C | | **O** | | | | C | C |
| RPT-026 | | | | C | | **O** | | | C | C | | | | |
| RPT-027 | | | | **O** | C | **O** | | | | | | | | C |
| RPT-028 | | | | C | C | **O** | | | | | | | | C |
| RPT-029 | | | | | C | **O** | | | | | | | | C |
| RPT-030 | C | | | C | | **O** | | | | C | C | | | |
| RPT-031 | | C | C | | | | | | | | **O** | | | |
| RPT-032 | C | | | | | C | | | C | **O** | | | | |
| RPT-033 | | | | | | | C | | | **O** | | | | C |
| RPT-034 | C | C | | C | C | | | | | | | | **O** | C |
| RPT-035 | C | C | | | | | | | | | | | **O** | C |
| RPT-036 | C | | | | | C | C | | | | | C | | **O** |
| RPT-037 | C | | | | | C | C | | C | C | | | | **O** |
| RPT-038 | | | | | C | | | | | | | **O** | | C |
| RPT-039 | C | | | | C | | | | | | | **O** | | C |
| RPT-040 | | C | | | | | C | | | | | | | C |

**O** owner · **C** consumer

## Appendix B — Latency classes

| Class | SLO | Reports |
|---|---|---|
| Near real time | ≤ 5 minutes | RPT-024, RPT-032 |
| Sub-hourly | ≤ 15 minutes | RPT-020, RPT-028 |
| Intraday | ≤ 60 minutes | RPT-019, RPT-026 |
| Four-hourly | ≤ 4 hours | RPT-021 |
| Next business day | T+1 | RPT-002 (daily metrics), RPT-003, RPT-006, RPT-007, RPT-008, RPT-012, RPT-017, RPT-018, RPT-022, RPT-023, RPT-025, RPT-027, RPT-031, RPT-033, RPT-038, RPT-040 |
| Close-cycle | T+3 to T+7 | RPT-004, RPT-005, RPT-013, RPT-014, RPT-015, RPT-029, RPT-030, RPT-034, RPT-035, RPT-037 |
| Board and regulatory | T+4 to deadline | RPT-001, RPT-009, RPT-010, RPT-011, RPT-016, RPT-036, RPT-039 |

RPT-012 sits in the next-business-day class but with a hard clock time of 09:00 rather than an elapsed budget. It is the only report in the set with that property.
