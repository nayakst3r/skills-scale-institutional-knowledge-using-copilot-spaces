# 02 — Business Specifications

**Document ID:** OAFG-BSR-2026-02 · **Version:** 1.0 · **Owner:** Head of Business Analysis
**Approvers:** P-01 (risk rules), P-04 (liquidity and capital rules), P-06 (finance rules), P-07 (financial crime rules), P-12 (data quality rules)

---

## 0. How to read a business rule

Every rule uses the same structure. A rule that cannot be stated in this structure is not yet a requirement.

| Field | Meaning |
|---|---|
| **Statement** | The rule in business language. Binding. |
| **Source** | The exact `schema.table.column` inputs from `banking_ecm`. If a column is not named here, it is not an input. |
| **Logic** | Executable pseudo-SQL. Ambiguity here is a defect in this document, not a decision for the implementer. |
| **Edges** | Named edge cases with their required treatment. Silence on an edge case is a defect. |
| **Control** | The `CTL-nnn` control that proves the rule operates, and the accountable persona. |
| **Test** | The `AC-nnn` acceptance criterion in [07](./07-acceptance-criteria-and-test-plan.md). |

Where a rule produces a certified metric, the metric identifier is given. **The metric definition lives in [05](./05-semantic-layer-and-metrics.md) and is not restated anywhere else.**

Severity of violation:

| Severity | Meaning | Response |
|---|---|---|
| **Blocking** | Report must not publish; submission must not file | Pipeline halts, incident raised |
| **Qualifying** | Report publishes with a visible qualification banner | Recorded on `RPT-038`, remediation tracked |
| **Advisory** | Recorded, trended, not blocking | Reviewed at the monthly steward forum |

---

# Part A — Credit Risk

## BR-CRR-001 — Exposure population definition

**Statement.** The group credit exposure population for a reporting date is every row in `risk.credit_exposure` whose `measurement_date` equals the reporting date and whose `exposure_status` is not `cancelled`, joined to a party that exists and is not in `prospect` lifecycle status. No other population is ever used for group credit reporting.

**Source.** `risk.credit_exposure` (`measurement_date`, `exposure_status`, `party_id`, `ead`, `net_exposure`, `current_exposure`), `customer.party` (`party_id`, `lifecycle_status`).

**Logic.**
```sql
SELECT e.*
FROM banking_ecm.risk.credit_exposure e
JOIN banking_ecm.customer.party p ON p.party_id = e.party_id
WHERE e.measurement_date = :as_of_date
  AND e.exposure_status <> 'cancelled'
  AND p.lifecycle_status <> 'prospect'
```

**Edges.**
- A facility approved but never drawn still has exposure through undrawn commitment. It is in population. See `BR-CRR-006`.
- An exposure whose `party_id` has no matching party row is a blocking data quality failure under `BR-DQ-002`, never a silent exclusion.
- Exposures to internal legal entities (`customer.party` rows flagged as OAFG entities) are excluded from external concentration but included in solo-entity reporting. The consolidation filter, not the population filter, handles this.

**Control.** `CTL-001`, owner P-02. **Test.** `AC-011`.

---

## BR-CRR-002 — Exposure measure hierarchy

**Statement.** Three exposure measures exist and are never used interchangeably. Every report must state which it uses.

| Measure | Column | Meaning | Used for |
|---|---|---|---|
| Current exposure | `current_exposure` | Drawn balance plus accrued, no add-on | Operational monitoring |
| Net exposure | `net_exposure` | Current exposure after netting and eligible collateral | Limit monitoring, concentration |
| Exposure at default | `ead` | Regulatory EAD including CCF on undrawn and PFE on derivatives | Capital, ECL, large exposure |

**Source.** `risk.credit_exposure` (`current_exposure`, `net_exposure`, `ead`, `potential_future_exposure`, `expected_exposure`, `collateral_value`).

**Logic.** `net_exposure = current_exposure - LEAST(collateral_value, current_exposure)` after netting-set offset. A row where `net_exposure > current_exposure` fails validation. A row where `net_exposure < 0` is clamped to zero for reporting and flagged advisory.

**Edges.**
- Over-collateralised exposures produce zero net exposure but non-zero EAD. Both are correct; a report showing zero risk on an over-collateralised derivative is wrong.
- Netting is applied at `netting_set_id`, never at party level. Two exposures to the same party in different netting sets do not offset.

**Control.** `CTL-001`, owner P-02. **Test.** `AC-012`.

---

## BR-CRR-003 — Connected client group aggregation

**Statement.** Concentration and large exposure are measured against the **connected client group**, not the individual legal entity. A connected client group is the transitive closure of `customer.relationship_hierarchy` under control relationships, plus any economic dependency link recorded in `customer.party_relationship`.

**Source.** `customer.relationship_hierarchy`, `customer.party_relationship`, `customer.party` (`party_id`, `legal_name`).

**Logic.** Recursive traversal to a maximum depth of 12 levels. The group identifier is the `party_id` of the ultimate parent, defined as the node with no inbound control edge. Cycles are impossible by model construction (the ECM guarantees no FK cycles) but a cycle in the *data* is a blocking failure under `BR-DQ-003`.

**Edges.**
- A party with two ultimate parents (joint control) is assigned to both groups. Its exposure counts in full against each group's limit. It is counted once at group total, using the greater group assignment, and the double count is disclosed on `RPT-003`.
- Economic dependency without ownership (a supplier whose failure would cause the borrower's failure) is included only where a credit analyst has recorded it. It is never inferred.
- A group whose depth exceeds 12 levels raises a blocking failure rather than silently truncating.

**Control.** `CTL-002`, owner P-02. **Test.** `AC-013`.

---

## BR-CRR-004 — Large exposure identification

**Statement.** An exposure to a connected client group is a large exposure when the group's aggregate EAD, after eligible credit risk mitigation, equals or exceeds 10 % of eligible tier 1 capital at the reporting consolidation level.

**Source.** `risk.credit_exposure` (`ead`, `large_exposure_flag`, `party_id`), `treasury.capital_ratio` (`tier1_capital_amount`, `consolidation_level`, `reporting_date`), connected group from `BR-CRR-003`.

**Logic.**
```sql
SUM(e.ead) OVER (PARTITION BY connected_group_id)
  >= 0.10 * (SELECT tier1_capital_amount
             FROM banking_ecm.treasury.capital_ratio
             WHERE reporting_date = :as_of_date
               AND consolidation_level = :level)
```

**Edges.**
- Tier 1 capital for a date where `treasury.capital_ratio` has no row is a blocking failure. The prior period's capital is never substituted, because it understates the ratio in a growing book and overstates it in a shrinking one.
- A group crossing the threshold intra-period is reported from the date it crossed, not from period end.
- `large_exposure_flag` on the source row is treated as an assertion to be verified, not as the answer. A disagreement between the stored flag and the calculated result is a qualifying failure reported on `RPT-003`.

**Control.** `CTL-002`, owner P-02. **Test.** `AC-014`. **Metric.** `MET-017`.

---

## BR-CRR-005 — Concentration measurement across five dimensions

**Statement.** Concentration is measured simultaneously across counterparty, industry, geography, product and collateral type. A portfolio that is inside limit on every single dimension may still be outside appetite in combination, so combination breaches are reported separately.

**Source.** `risk.concentration_risk` (`concentration_dimension`, `concentration_type`, `concentration_percentage`, `hhi_index_value`, `current_exposure_amount`, `limit_threshold`, `warning_threshold`, `breach_status`, `measurement_date`), `reference.industry_code`, `reference.geographic_region`, `reference.product_type`, `collateral.collateral_asset`.

**Logic.** For each dimension `d` and each value `v`:
- `concentration_percentage = SUM(ead) WHERE dimension_value = v / SUM(ead) over the whole population`
- `hhi_index_value = SUM(share_v ^ 2) * 10000` across all values of `d`, where `share_v` is the proportion of exposure held by value `v`

HHI bands: below 1500 unconcentrated, 1500 to 2500 moderately concentrated, above 2500 highly concentrated. Band transitions are reportable events regardless of whether a limit was breached.

**Edges.**
- Unclassified exposures (null industry, null geography) form their own bucket named `UNCLASSIFIED`. They are never excluded from the denominator, because excluding them flatters concentration. A `UNCLASSIFIED` bucket above 2 % of the portfolio is a qualifying data quality failure.
- Combination concentration is measured for the six pairs the risk appetite names: industry × geography, industry × product, geography × product, counterparty × collateral type, product × collateral type, industry × collateral type.

**Control.** `CTL-002`, owner P-02. **Test.** `AC-015`. **Metric.** `MET-018`.

---

## BR-CRR-006 — Credit conversion factor on undrawn commitment

**Statement.** Undrawn committed amounts convert to EAD using the regulatory CCF applicable to the facility type and the regulatory approach in force for the entity.

**Source.** `loan.facility` (`committed_amount`, `drawn_amount`, `undrawn_amount`, `facility_type`, `facility_status`), `risk.credit_exposure` (`ead`, `regulatory_approach`), `risk.irb_model` (`ead_ccf_estimate`, `model_status`, `regulatory_approval_status`).

**Logic.**
```
undrawn := GREATEST(committed_amount - drawn_amount, 0)
ccf     := CASE regulatory_approach
             WHEN 'IRB_ADVANCED' THEN irb_model.ead_ccf_estimate
             ELSE standardised_ccf(facility_type, uncommitted_flag, original_maturity)
           END
ead     := drawn_amount + (undrawn * ccf)
```

**Edges.**
- `undrawn_amount` stored on `loan.facility` is verified against `committed_amount - drawn_amount`. A difference greater than USD 1 is a qualifying failure; the derived value is used.
- Unconditionally cancellable facilities take a CCF floor per the applicable regime, never zero, under Basel III finalisation.
- An advanced-IRB CCF from a model whose `regulatory_approval_status` is not approved must not be used. The rule falls back to standardised and raises a blocking failure under `BR-MDL-004`.
- Facilities in `facility_status` of `cancelled` or `expired` contribute zero undrawn.

**Control.** `CTL-004`, owner P-02. **Test.** `AC-016`.

---

## BR-CRR-007 — Internal rating currency

**Statement.** An internal counterparty rating is current when its `rating_status` is active, `effective_date` is on or before the reporting date, `expiry_date` is null or after the reporting date, and `next_review_date` has not passed.

**Source.** `risk.counterparty_rating` (`rating_code`, `rating_status`, `effective_date`, `expiry_date`, `next_review_date`, `rating_date`, `pd`, `lgd`, `analyst_override_flag`, `override_direction`, `override_reason`, `rating_committee_approval`).

**Logic.** Where multiple ratings satisfy the currency test for one party, the one with the latest `rating_date` wins; ties break on the highest `counterparty_rating_id`. An expired rating is not replaced by an external agency rating automatically.

**Edges.**
- A rating past `next_review_date` is **stale**. Stale ratings continue to be used for exposure reporting but are excluded from new origination eligibility and are reported on `RPT-005`.
- A stale rating older than 18 months forces the exposure into the standardised approach for capital, per `BR-CAP-007`.
- A party with no rating at all is assigned the unrated treatment and flagged. It is never assigned a default rating.

**Control.** `CTL-005`, owner P-03. **Test.** `AC-017`.

---

## BR-CRR-008 — Rating override governance

**Statement.** An analyst override of a model-produced rating is valid only when it carries a recorded direction, a recorded reason, and committee approval. An override without all three is invalid, and the model rating applies.

**Source.** `risk.counterparty_rating` (`analyst_override_flag`, `override_direction`, `override_reason`, `rating_committee_approval`, `prior_rating_code`, `rating_methodology`), `customer.party_risk_rating` (`override_flag`, `override_rationale`).

**Logic.**
```sql
CASE
  WHEN analyst_override_flag
   AND override_direction IS NOT NULL
   AND override_reason IS NOT NULL
   AND rating_committee_approval
  THEN rating_code
  ELSE model_produced_rating
END
```

**Edges.**
- Upward overrides (improving the rating) above two notches require CRO approval. The absence of that approval makes the override invalid, not merely exceptional.
- Override rate is monitored per analyst and per model under `BR-MDL-003`. A sustained override rate above 15 % on any model is a model performance signal, not an analyst performance signal, and is escalated to P-13.

**Control.** `CTL-005`, owner P-13. **Test.** `AC-018`. **Metric.** `MET-048`.

---

## BR-CRR-009 — Watchlist entry triggers

**Statement.** A counterparty enters the watchlist automatically when any of the following occurs, and exits only by explicit approved decision.

| Trigger | Condition | Source |
|---|---|---|
| Rating downgrade | Two or more notches in 90 days | `risk.counterparty_rating.prior_rating_code`, `rating_change_date` |
| Stage migration | Movement to IFRS 9 stage 2 or 3 | `risk.risk_ecl_provision.ifrs9_stage` |
| Delinquency | `days_past_due` ≥ 30 on any facility | `loan.loan_account.days_past_due` |
| Covenant breach | Any breach not waived | `loan.covenant.covenant_status`, `waiver_granted_flag` |
| Collateral shortfall | Coverage ratio below 100 % for 5 consecutive business days | `loan.loan_account.collateral_coverage_ratio` |
| Forbearance | Any forbearance granted | `loan.loan_account.forbearance_flag` |
| External signal | External rating downgrade or negative outlook | `risk.counterparty_rating.external_rating_date`, `rating_outlook` |
| Market signal | CDS spread widening beyond threshold where observable | External feed via `reference.market_data_source` |

**Edges.**
- Automatic entry cannot be suppressed. It can only be exited by a recorded decision with an approver, which becomes an audit artefact.
- A counterparty exiting the watchlist re-enters immediately if the trigger condition still holds. Exit therefore requires the condition to have cleared, not merely a view that it will.
- Entry triggered by a data quality error is corrected by fixing the data, which removes the trigger. Manual suppression of a trigger is prohibited.

**Control.** `CTL-006`, owner P-02. **Test.** `AC-019`.

---

## BR-CRR-010 — Non-performing classification

**Statement.** A loan account is non-performing when it is 90 or more days past due, **or** is classified as unlikely to pay regardless of days past due, **or** has been charged off in part.

**Source.** `loan.loan_account` (`days_past_due`, `npl_classification`, `npl_classification_date`, `npl_trigger_event`, `charge_off_amount`, `forbearance_flag`), `risk.risk_ecl_provision` (`npl_classification`, `npl_entry_date`, `default_flag`, `cure_status`).

**Logic.**
```
is_npl := (CAST(days_past_due AS INT) >= 90)
       OR (npl_trigger_event IN ('unlikely_to_pay','bankruptcy','restructure_loss'))
       OR (charge_off_amount > 0)
```

**Edges.**
- **Contagion.** Where non-performing exposure to a single obligor exceeds 20 % of that obligor's total on-balance-sheet exposure, all of that obligor's exposures become non-performing. This is the rule most often missed and is explicitly in scope.
- **Cure.** Exit from non-performing requires a minimum 12-month probation with no arrears and no forbearance concession. `cure_status` records the probation state. Early exit is prohibited.
- **Forborne non-performing.** A forborne exposure that is cured remains flagged as forborne performing for a further 24 months and is separately reported.
- `days_past_due` is stored as `STRING` in the model and must be cast defensively. A non-numeric value is a blocking failure under `BR-DQ-005`.

**Control.** `CTL-007`, owner P-02. **Test.** `AC-020`. **Metric.** `MET-011`.

---

## BR-CRR-011 — Limit utilisation and breach

**Statement.** Limit utilisation is measured against the limit's own utilisation basis, not against a single group-wide exposure measure. A limit expressed on net exposure is never tested against EAD.

**Source.** `risk.risk_limit` (`limit_code`, `limit_type`, `amount`, `currency`, `current_utilization_amount`, `utilization_pct`, `utilization_basis`, `warning_threshold_pct`, `hard_stop_flag`, `breach_action_rule`, `escalation_level_1`, `escalation_level_2`, `limit_status`, `effective_date`, `expiry_date`).

**Logic.** `utilization_pct = current_utilization_amount / amount`, computed in the limit's own `currency` after translating exposure at the `FX-02` rate. Status bands: green below `warning_threshold_pct`, amber between warning and 100 %, red at or above 100 %.

**Edges.**
- A hard-stop limit at or above 100 % blocks new origination against that limit immediately. This is a system-enforced consequence, not a reporting observation.
- A limit whose `expiry_date` has passed but whose utilisation is non-zero is a blocking governance failure. Exposure does not expire because a limit did.
- Utilisation above 100 % caused by FX movement rather than new exposure is separately identified on `RPT-003`, because the management response differs.
- Where `current_utilization_amount` on the source row disagrees with the recomputed utilisation by more than USD 1,000, the recomputed value is used and a qualifying failure is raised.

**Control.** `CTL-008`, owner P-01. **Test.** `AC-021`. **Metric.** `MET-019`.

---

## BR-CRR-012 — Risk appetite status determination

**Statement.** Each risk appetite metric has a red, amber and green threshold with an explicit direction. Status is computed, never asserted, and an amber or red status triggers the escalation the appetite statement itself specifies.

**Source.** `risk.appetite` (`metric_name`, `metric_definition`, `limit_value`, `threshold`, `tolerance_threshold`, `warning_threshold`, `direction`, `breach_escalation_level`, `breach_response_timeframe_days`, `is_board_approved`, `effective_date`, `expiry_date`, `governance_body`), `risk.kri_measurement` (`kri_code`, `actual_value`, `green_threshold`, `amber_threshold`, `red_threshold`, `threshold_direction`, `breach_status`, `measurement_date`).

**Logic.** For `threshold_direction = 'upper'` a higher value is worse; for `'lower'` a lower value is worse. Status is derived by comparing `actual_value` against the bands in the direction's sense. A metric with a null threshold in the relevant band is a blocking failure, because an appetite metric with no threshold is not an appetite metric.

**Edges.**
- An appetite metric whose `expiry_date` has passed without a successor is a blocking governance failure reported directly to P-01.
- Only metrics with `is_board_approved` true appear on the Board pack. Others appear on management reporting.
- A red status must show, in the same view, the escalation required by `breach_escalation_level` and the deadline derived from `breach_response_timeframe_days`. Showing the breach without the required response is a specification failure.

**Control.** `CTL-009`, owner P-01. **Test.** `AC-022`. **Metric.** `MET-020`.

---

## BR-CRR-013 — Covenant testing and breach

**Statement.** A covenant is tested at its stated frequency against the stated financial statement source. A test that could not be performed because the financial information was not delivered is a **reporting breach**, distinct from a **financial breach**, and both are tracked.

**Source.** `loan.covenant` (`covenant_name`, `covenant_type`, `covenant_category`, `threshold_value`, `threshold_operator`, `threshold_unit`, `measurement_frequency`, `measurement_basis`, `financial_statement_source`, `reporting_deadline_days`, `grace_period_days`, `covenant_status`, `waiver_granted_flag`, `waiver_effective_date`, `waiver_expiration_date`, `cross_default_flag`, `cure_provision_flag`, `cure_mechanism`, `materiality_classification`, `facility_id`).

**Logic.**
```
breach := NOT compare(actual_value, threshold_operator, threshold_value)
effective_breach := breach
                AND NOT (waiver_granted_flag
                         AND :test_date BETWEEN waiver_effective_date AND waiver_expiration_date)
                AND :test_date > covenant_test_date + grace_period_days
reporting_breach := financial_information_received_date IS NULL
                AND :test_date > period_end + reporting_deadline_days
```

**Edges.**
- **Cross-default.** A breach on a covenant with `cross_default_flag` true propagates to every other facility of the same obligor. The propagated breach is reported as such, with its origin identified.
- An expired waiver reinstates the breach automatically on the day after expiry.
- A covenant with `materiality_classification` of immaterial still generates a breach record; it simply does not trigger escalation.
- Near-breach reporting is mandatory: any covenant within 10 % of its threshold appears on `RPT-007` before it breaches.

**Control.** `CTL-010`, owner P-03. **Test.** `AC-023`. **Metric.** `MET-021`.

---

## BR-CRR-014 — Origination quality and vintage tracking

**Statement.** Every credit application decision is retained with the decision inputs as they stood at decision time, so that origination quality can be assessed by vintage without hindsight contamination.

**Source.** `loan.credit_application` (`application_number`, `application_status`, `application_type`, `application_channel`, `requested_amount`, `approved_amount`, `approved_interest_rate`, `credit_score`, `dscr`, `ltv_ratio`, `underwriting_decision`, `decline_reason`, `credit_committee_approval_date`, `pipeline_stage`, `kyc_completed`, `aml_screening_status`, `application_submitted_timestamp`), `loan.facility` (`origination_date`, `facility_number`).

**Logic.** Vintage cohort is the calendar quarter of `origination_date`. Cohort performance is measured at 6, 12, 24 and 36 months on: 90+ day delinquency rate, stage 2 migration rate, charge-off rate, and average rating migration.

**Edges.**
- An application approved but never drawn is excluded from vintage performance and reported separately as approval leakage.
- Policy exceptions at origination must be identifiable, because vintage analysis that cannot separate policy-compliant from exception lending is not decision-useful.
- Applications where `kyc_completed` is false or `aml_screening_status` is not cleared must never reach approved status. A drawn facility behind an uncleared application is a blocking compliance failure escalated to P-07.

**Control.** `CTL-004`, owner P-02. **Test.** `AC-024`.

---

# Part B — Impairment (IFRS 9 and CECL)

## BR-IMP-001 — Dual measurement basis

**Statement.** OAFG measures impairment under IFRS 9 for group and EU reporting and under ASC 326 (CECL) for US entity reporting. Both run on the same exposure population from `BR-CRR-001`. Neither is derived from the other. The difference between them is explained, not eliminated.

**Source.** `risk.risk_ecl_provision` (`ifrs9_stage`, `ecl_12month_amount`, `ecl_lifetime_amount`, `cecl_pool_classification`, `provision_amount`, `reporting_date`, `portfolio_segment`, `collective_assessment_flag`), `loan.loan_ecl_provision`.

**Logic.** IFRS 9 provision equals `ecl_12month_amount` for stage 1 and `ecl_lifetime_amount` for stages 2 and 3. CECL provision is lifetime expected loss for every exposure regardless of stage. The reported `provision_amount` carries the basis applicable to the reporting entity.

**Edges.**
- A US entity consolidated into the group reports CECL locally and IFRS 9 into the group. Both figures exist for the same exposure on the same date and both are correct.
- The IFRS 9 to CECL bridge is a mandatory disclosure on `RPT-004` and must reconcile to the last cent.

**Control.** `CTL-012`, owner P-06. **Test.** `AC-031`. **Metric.** `MET-008`.

---

## BR-IMP-002 — Stage 1 to stage 2 transfer, significant increase in credit risk

**Statement.** An exposure transfers to stage 2 when there has been a significant increase in credit risk since initial recognition. SICR is assessed on a quantitative test, a set of qualitative triggers, and a backstop, in that order. **Any one is sufficient.**

**Source.** `risk.risk_ecl_provision` (`sicr_flag`, `pd_12month`, `pd_lifetime`, `origination_date`, `stage_migration_date`, `days_past_due`, `forbearance_flag`, `ifrs9_stage`, `portfolio_segment`), `risk.counterparty_rating` (`rating_code`, `prior_rating_code`, `pd`), `loan.loan_account` (`days_past_due`, `forbearance_flag`, `watch_list_date`).

**Logic.**

*Quantitative test.* SICR is triggered when lifetime PD has increased relative to origination beyond the segment's threshold, measured both relatively and absolutely:
```
relative_trigger := (pd_lifetime / pd_lifetime_at_origination) >= segment_relative_multiple
absolute_trigger := (pd_lifetime - pd_lifetime_at_origination) >= segment_absolute_bps
quantitative_sicr := relative_trigger AND absolute_trigger
```
Segment thresholds (`portfolio_segment` on `risk.risk_ecl_provision`):

| Segment | Relative multiple | Absolute increase | Low credit risk exemption |
|---|---|---|---|
| Retail mortgage | 2.0× | 50 bps | Not applied |
| Retail unsecured | 1.8× | 200 bps | Not applied |
| SME | 2.0× | 100 bps | Not applied |
| Corporate investment grade | 2.5× | 30 bps | Applied |
| Corporate sub-investment grade | 2.0× | 100 bps | Not applied |
| Sovereign and bank | 3.0× | 15 bps | Applied |

*Qualitative triggers.* Any of: forbearance granted; watchlist entry under `BR-CRR-009`; internal rating downgrade of three or more notches; covenant breach not waived; a going-concern qualification in audited accounts.

*Backstop.* 30 days past due. The backstop is rebuttable only with documented evidence approved by P-02, and rebuttals are capped at 5 % of the stage 2 population by balance. A rebuttal rate above the cap is a blocking governance failure.

**Edges.**
- **PD at origination must be retained.** An exposure whose origination PD is unavailable cannot be quantitatively tested and falls back to qualitative triggers and the backstop, and is reported as such on `RPT-005`. Silently defaulting such exposures to stage 1 is prohibited.
- The low credit risk exemption applies only where the exposure is investment grade at the reporting date, and is disallowed entirely for any exposure that has ever been stage 2.
- SICR is assessed at instrument level, not obligor level, except where obligor-level contagion under `BR-CRR-010` applies.
- Stage 2 entry driven solely by the 30-day backstop must be separately reported, because P-02 explicitly asks for this and because a portfolio whose stage 2 is mostly backstop-driven has a model problem.

**Control.** `CTL-012`, owner P-02. **Test.** `AC-032`. **Metric.** `MET-010`.

---

## BR-IMP-003 — Stage 3 and credit-impaired definition

**Statement.** Stage 3 is aligned to the non-performing definition in `BR-CRR-010`. There is no separate impairment definition of default. A difference between the stage 3 population and the non-performing population is a blocking reconciliation failure.

**Source.** `risk.risk_ecl_provision` (`ifrs9_stage`, `default_flag`, `npl_classification`), `loan.loan_account` (`npl_classification`).

**Logic.** `ifrs9_stage = '3' IFF is_npl` per `BR-CRR-010`, with the single exception of POCI assets under `BR-IMP-004`.

**Control.** `CTL-012`, owner P-02. **Test.** `AC-033`.

---

## BR-IMP-004 — Purchased or originated credit-impaired assets

**Statement.** POCI assets never enter the staging model. They are measured at lifetime ECL from initial recognition and remain POCI for life, including after cure.

**Source.** `risk.risk_ecl_provision` (`poci_flag`, `ecl_lifetime_amount`, `ifrs9_stage`, `origination_date`).

**Logic.** Where `poci_flag` is true, `ifrs9_stage` is reported as `POCI`, not as 1, 2 or 3. Provision movement is the change in lifetime ECL, favourable or adverse, recognised in P&L.

**Edges.**
- A POCI asset showing a stage of 1, 2 or 3 is a blocking failure.
- A POCI asset that cures does not move to stage 1. This is the most commonly implemented error in IFRS 9 and is called out explicitly.

**Control.** `CTL-012`, owner P-06. **Test.** `AC-034`.

---

## BR-IMP-005 — Expected credit loss calculation

**Statement.** ECL is the probability-weighted present value of cash shortfalls, computed as the sum over scenarios and time periods of PD × LGD × EAD, discounted at the effective interest rate.

**Source.** `risk.risk_ecl_provision` (`pd_12month`, `pd_lifetime`, `lgd_estimate`, `ead_amount`, `discount_rate`, `ecl_12month_amount`, `ecl_lifetime_amount`, `macro_scenario_weight`, `macro_overlay_factor`, `recovery_expectation_amount`, `collateral_value`, `ltv_ratio`, `maturity_date`, `origination_date`).

**Logic.**
```
ECL_scenario_s = SUM over t in 1..T of
                   marginal_PD(t, s) * LGD(t, s) * EAD(t, s) / (1 + discount_rate)^t
ECL            = SUM over s of macro_scenario_weight(s) * ECL_scenario_s
ECL_reported   = ECL * macro_overlay_factor
```
where `T` is 12 months for stage 1 and the remaining behavioural life for stages 2 and 3.

**Edges.**
- `SUM(macro_scenario_weight)` across scenarios must equal 1.0000 within a tolerance of 0.0001. Otherwise blocking.
- Behavioural life for revolving facilities without a contractual maturity uses the segment's behavioural life assumption, which must be a documented, model-validated input, never a hard-coded constant.
- `macro_overlay_factor` other than 1.0 requires the post-model adjustment governance in `BR-IMP-008`. An unapproved overlay is blocking.
- The discount rate is the original effective interest rate, not the current rate. Using the current rate is a defect.

**Control.** `CTL-012`, owner P-02. **Test.** `AC-035`. **Metric.** `MET-008`.

---

## BR-IMP-006 — Macroeconomic scenario weighting

**Statement.** ECL uses a minimum of three forward-looking macroeconomic scenarios: base, upside and downside, with a fourth severe downside where the portfolio's non-linearity requires it. Weights are approved quarterly by the Impairment Committee and are identical across all portfolios in a reporting period.

**Source.** `risk.risk_ecl_provision` (`macro_scenario_weight`, `stress_scenario_id`), `risk.stress_scenario`, `risk.scenario_result`.

**Edges.**
- Different scenario weights applied to different portfolios in the same period is a blocking failure. It is the classic route to unauditable provisioning.
- Weight changes between periods must be explained in the ECL movement attribution under `BR-IMP-009`.

**Control.** `CTL-012`, owner P-02. **Test.** `AC-036`.

---

## BR-IMP-007 — Collateral in LGD

**Statement.** Collateral reduces LGD only where it is eligible, legally enforceable, currently valued and correctly haircut. Stale or unenforceable collateral is treated as absent.

**Source.** `collateral.collateral_asset`, `collateral.collateral_valuation` (`valuation_date`, `valuation_amount`, `valuation_method`), `collateral.haircut_schedule` (`haircut_percentage`), `collateral.eligibility_rule`, `collateral.lien_filing`, `risk.risk_ecl_provision` (`lgd_estimate`, `collateral_value`, `recovery_expectation_amount`).

**Logic.** `eligible_collateral_value = valuation_amount * (1 - haircut_percentage)`, applied only where the valuation is within the asset class's maximum valuation age and where a perfected lien exists.

Maximum valuation age by asset class:

| Asset class | Maximum age | Treatment when exceeded |
|---|---|---|
| Cash and marketable securities | 1 business day | Value set to zero |
| Residential real estate | 12 months | Indexed value used, additional 10 % haircut |
| Commercial real estate | 12 months | Indexed value used, additional 15 % haircut |
| Plant, equipment and inventory | 6 months | Value set to zero |
| Receivables | 3 months | Value set to zero |

**Edges.**
- Collateral pledged against multiple exposures is allocated, never double counted. Allocation is pro rata to EAD unless a priority ranking is recorded.
- A lien filing that has lapsed removes eligibility from the lapse date, not from the date it is noticed.
- Indexation is permitted for real estate only, using an approved index, and the indexed value never exceeds the last physical appraisal by more than 20 %.

**Control.** `CTL-013`, owner P-02. **Test.** `AC-037`.

---

## BR-IMP-008 — Post-model adjustments and overlays

**Statement.** Any adjustment to model-produced ECL requires a documented rationale, a quantified basis, a named approver, an expiry date and a defined path to model remediation. Overlays without an expiry are prohibited.

**Source.** `risk.risk_ecl_provision` (`macro_overlay_factor`, `provision_amount`, `provision_status`), `risk.model_validation`, `audit.management_action`.

**Edges.**
- An overlay in place for more than four consecutive quarters is automatically escalated to P-13 as a model deficiency, and to P-14 as a control observation.
- Overlays are disclosed at portfolio segment level on `RPT-004`, showing model output, overlay and final provision separately. Presenting only the final number is prohibited.
- The aggregate overlay as a percentage of total ECL is a board-reported metric.

**Control.** `CTL-012`, owner P-02 and P-13 jointly. **Test.** `AC-038`.

---

## BR-IMP-009 — ECL movement attribution

**Statement.** The change in ECL between two reporting dates is fully attributed to named causes that sum exactly to the total movement. An unexplained residual is a defect, not a rounding item.

**Source.** `risk.risk_ecl_provision` at two reporting dates, `provision_movement_amount`, `write_off_amount`, `stage_migration_date`.

**Attribution order.** Sequence matters, because the categories are not commutative.

| # | Cause | Definition |
|---|---|---|
| 1 | New origination | Exposures present at `t1` and absent at `t0` |
| 2 | Derecognition | Exposures present at `t0` and absent at `t1`, other than write-offs |
| 3 | Write-off | `write_off_amount` recognised in the period |
| 4 | Stage transfer | ECL change attributable to a change in `ifrs9_stage`, holding risk parameters at `t0` |
| 5 | Risk parameter change | Change in PD, LGD or EAD, holding stage at `t1` |
| 6 | Scenario and weight change | Change in `macro_scenario_weight` or scenario definitions |
| 7 | Overlay change | Change in `macro_overlay_factor` |
| 8 | Model change | New or recalibrated model deployed in the period |
| 9 | Foreign exchange | Retranslation at closing rates |
| 10 | Residual | Must be zero. Non-zero is a blocking failure. |

**Control.** `CTL-012`, owner P-02. **Test.** `AC-039`.

---

## BR-IMP-010 — Risk and finance provision reconciliation

**Statement.** The provision balance in the risk system must equal the provision balance in the general ledger for every legal entity and every reporting date, within materiality.

**Source.** `risk.risk_ecl_provision` (`provision_amount`, `journal_entry_id`), `loan.loan_ecl_provision`, `ledger.journal_entry`, `ledger.journal_entry_line`, `ledger.gl_account`.

**Logic.** Sum risk provision by legal entity and compare to the sum of provision-account GL balances. Every risk provision row must carry a `journal_entry_id`; a row without one is unposted and is a blocking failure at close.

**Edges.**
- Timing differences between risk close and finance close are permitted only within the close calendar window and must clear before sign-off.
- The reconciliation runs at three grains: legal entity, portfolio segment and GL account. A reconciliation that ties only at the top is not evidence.

**Control.** `CTL-015`, owner P-06. **Test.** `AC-040`.

---

## BR-IMP-011 — Stage override governance

**Statement.** A manual override of a computed IFRS 9 stage requires a recorded reason, evidence, an approver independent of the proposer, and an expiry. Downward overrides (to a better stage) additionally require P-02 approval.

**Source.** `risk.risk_ecl_provision` (`ifrs9_stage`, `provision_status`, `sicr_flag`), `audit.management_action`.

**Edges.**
- Override volume is capped at 3 % of stage 2 and stage 3 populations by balance. Exceeding the cap is a blocking governance failure requiring CRO acceptance.
- Overrides are always disclosed on `RPT-004` and `RPT-005`, both in count and in ECL impact.

**Control.** `CTL-012`, owner P-02. **Test.** `AC-041`.

---

## BR-IMP-012 — Write-off recognition

**Statement.** A write-off is recognised when there is no reasonable expectation of recovery. Write-off reduces gross carrying amount and the associated provision simultaneously, and never creates a P&L charge on its own.

**Source.** `risk.risk_ecl_provision` (`write_off_amount`), `loan.write_off`, `loan.loan_account` (`charge_off_amount`, `charge_off_date`), `ledger.journal_entry`.

**Edges.**
- Partial write-offs are permitted and must not remove the exposure from the population.
- Post-write-off recoveries are recognised as they occur and are reported separately from provision releases. Netting them into provision movement is prohibited.
- A write-off without a corresponding provision release of equal amount is a blocking reconciliation failure.

**Control.** `CTL-015`, owner P-06. **Test.** `AC-042`. **Metric.** `MET-014`.

---

# Part C — Regulatory Capital

## BR-CAP-001 — Capital ratio computation

**Statement.** Capital ratios are computed from capital components and risk-weighted assets at the stated consolidation level. A ratio is never taken from a source system without recomputation from its components.

**Source.** `treasury.capital_ratio` (`cet1_capital_amount`, `tier1_capital_amount`, `tier2_capital_amount`, `cet1_ratio`, `tier1_ratio`, `leverage_ratio`, `credit_rwa_amount`, `market_rwa_amount`, `operational_rwa_amount`, `consolidation_level`, `reporting_date`, `regulatory_minimum_cet1_ratio`, `capital_conservation_buffer`, `countercyclical_buffer`, `gsib_surcharge`).

**Logic.**
```
total_rwa := credit_rwa_amount + market_rwa_amount + operational_rwa_amount
cet1_ratio := cet1_capital_amount / total_rwa
tier1_ratio := tier1_capital_amount / total_rwa
total_capital_ratio := (tier1_capital_amount + tier2_capital_amount) / total_rwa
```

**Edges.**
- A recomputed ratio differing from the stored `cet1_ratio` by more than 1 basis point is a blocking failure. The recomputed value is authoritative.
- `total_rwa` of zero is a blocking failure, never a null ratio.
- Ratios are computed to four decimal places and compared to minima before any rounding, per `MAT-05`.

**Control.** `CTL-016`, owner P-04. **Test.** `AC-051`. **Metric.** `MET-001`, `MET-002`.

---

## BR-CAP-002 — Combined buffer requirement and maximum distributable amount

**Statement.** The combined buffer requirement is the sum of the capital conservation buffer, the institution-specific countercyclical buffer and any systemic surcharge. Breaching it restricts distributions.

**Source.** `treasury.capital_ratio` (`capital_conservation_buffer`, `countercyclical_buffer`, `gsib_surcharge`, `cet1_buffer_amount`, `planned_dividend_amount`, `planned_buyback_amount`, `regulatory_minimum_cet1_ratio`).

**Logic.**
```
combined_buffer := capital_conservation_buffer + countercyclical_buffer + gsib_surcharge
buffer_headroom := cet1_ratio - regulatory_minimum_cet1_ratio - combined_buffer
```
Where `buffer_headroom` is negative, the maximum distributable amount restriction applies and any `planned_dividend_amount` or `planned_buyback_amount` above the permitted quartile fraction is a blocking finding escalated to P-04 and P-01 the same day.

**Edges.**
- The countercyclical buffer is institution-specific, weighted by the geographic distribution of credit exposures. It is recomputed from `risk.credit_exposure.country_id` each quarter, not carried forward.
- Buffer headroom is reported both in ratio points and in absolute capital amount, because the management action differs.

**Control.** `CTL-016`, owner P-04. **Test.** `AC-052`.

---

## BR-CAP-003 — Credit risk-weighted assets

**Statement.** Credit RWA is computed per exposure using the approach approved for that exposure class and entity, then aggregated. Mixed-approach portfolios are aggregated after risk weighting, never before.

**Source.** `risk.credit_exposure` (`ead`, `risk_weight`, `rwa_credit`, `regulatory_approach`, `exposure_class`, `pd`, `lgd`, `effective_maturity_years`), `risk.irb_model` (`model_status`, `regulatory_approval_status`, `asset_class`, `pd_floor`, `downturn_lgd`).

**Logic.** For standardised exposures, `rwa_credit = ead * risk_weight`. For IRB exposures, `risk_weight` is derived from the supervisory formula using `pd`, `lgd` and `effective_maturity_years`, with regulatory floors applied to each input before the formula, not after.

**Edges.**
- PD floor is applied per `risk.irb_model.pd_floor` and never below the regulatory minimum for the asset class.
- `effective_maturity_years` is floored at 1 and capped at 5 for corporate exposures.
- An exposure whose `regulatory_approach` is advanced IRB but whose model is not approved falls back to standardised under `BR-MDL-004`, and the fallback is reported.
- `rwa_credit` stored on the source row is verified. A difference beyond 0.01 % is a qualifying failure.

**Control.** `CTL-016`, owner P-04. **Test.** `AC-053`. **Metric.** `MET-003`.

---

## BR-CAP-004 — Output floor

**Statement.** Total RWA computed under internal models is floored at the applicable percentage of the RWA that would result from full standardised computation. Both computations are produced every period, whether or not the floor binds.

**Source.** `risk.credit_exposure` (`rwa_credit`, `regulatory_approach`), `treasury.capital_ratio` (`credit_rwa_amount`, `market_rwa_amount`, `operational_rwa_amount`).

**Logic.** `reported_rwa = GREATEST(internal_model_rwa, floor_percentage * standardised_rwa)`.

**Edges.**
- The standardised parallel run is mandatory even in periods where the floor does not bind, because the trend towards binding is itself decision-useful and must be reported to P-04.
- When the floor binds, capital ratios are restated on the floored basis and the amount of the floor uplift is disclosed.

**Control.** `CTL-016`, owner P-04. **Test.** `AC-054`.

---

## BR-CAP-005 — Leverage ratio

**Statement.** The leverage ratio is tier 1 capital over total leverage exposure, which includes on-balance-sheet assets, derivative exposure, securities financing transaction exposure and off-balance-sheet items at their credit conversion factors.

**Source.** `treasury.capital_ratio` (`tier1_capital_amount`, `leverage_ratio`), `loan.facility` (`undrawn_amount`), `risk.credit_exposure` (`potential_future_exposure`), `treasury.repo_position`.

**Edges.**
- Off-balance-sheet items use leverage-specific CCFs, which differ from the credit RWA CCFs in `BR-CRR-006`. Reusing the credit CCF here is a defect.
- Collateral does not reduce leverage exposure except where explicitly permitted for securities financing transactions.

**Control.** `CTL-016`, owner P-04. **Test.** `AC-055`. **Metric.** `MET-004`.

---

## BR-CAP-006 — Stress testing execution and result capture

**Statement.** Each stress test run is a complete, immutable record of scenario, portfolio scope, model versions, execution parameters and results. A run cannot be partially superseded.

**Source.** `risk.stress_test_run` (`run_code`, `run_type`, `run_status`, `scenario_name`, `scenario_type`, `as_of_date`, `projection_end_date`, `stress_horizon_quarters`, `model_version`, `portfolio_scope_code`, `stressed_cet1_ratio`, `stressed_tier1_ratio`, `stressed_total_capital_ratio`, `stressed_leverage_ratio`, `stressed_rwa_amount`, `stressed_ecl_amount`, `stressed_ppnr_amount`, `stressed_nii_impact_amount`, `stressed_lcr_ratio`, `stressed_nsfr_ratio`, `stressed_var_amount`, `stressed_cva_amount`, `stress_capital_buffer_pct`, `capital_action_restriction_flag`, `regulatory_program`, `regulatory_outcome`, `approved_by`, `approval_timestamp`, `submission_reference`), `risk.stress_scenario`, `risk.scenario_result`, `risk.stress_test_factor_result`, `loan.stress_projection`.

**Edges.**
- A run with `run_status` other than complete must never appear in any report as a result. It may appear as a run-status observation.
- Re-running a scenario creates a new `run_code`. Overwriting a prior run is prohibited and is a severity-1 defect under `ARCH-05`.
- The minimum required scenario set is baseline, adverse and severely adverse. A submission with fewer is blocking.
- `capital_action_restriction_flag` true must propagate to `RPT-001` in the same cycle, because it constrains dividend decisions.

**Control.** `CTL-017`, owner P-01. **Test.** `AC-056`.

---

## BR-CAP-007 — Approach eligibility and fallback

**Statement.** An exposure may use an internal-model approach only when the model is approved, in force, validated within its frequency, and applicable to the exposure's asset class. Failing any condition, the standardised approach applies and the fallback is reported.

**Source.** `risk.irb_model` (`regulatory_approval_status`, `regulatory_approval_date`, `model_status`, `effective_from_date`, `effective_until_date`, `last_validation_date`, `next_validation_date`, `asset_class`, `use_in_rwa_calculation`, `use_in_ecl_calculation`).

**Logic.**
```
eligible := regulatory_approval_status = 'approved'
        AND model_status = 'active'
        AND :as_of_date BETWEEN effective_from_date AND COALESCE(effective_until_date, DATE'9999-12-31')
        AND :as_of_date <= next_validation_date
        AND use_in_rwa_calculation
        AND asset_class = exposure.exposure_class
```

**Edges.**
- Fallback to standardised almost always increases RWA. The capital impact of every fallback is quantified and reported to P-04 and P-13 the same cycle.
- A model past `next_validation_date` remains eligible only if MRM has granted a documented extension with an expiry. Silent extension is prohibited.

**Control.** `CTL-018`, owner P-13. **Test.** `AC-057`. **Metric.** `MET-047`.

---

## BR-CAP-008 — Capital allocation to business

**Statement.** Regulatory capital is allocated to lines of business in proportion to their contribution to RWA plus an operational risk allocation, and is the denominator of business-level return measures.

**Source.** `risk.credit_exposure` (`rwa_credit`), `treasury.capital_ratio`, `risk.operational_risk_event`, `ledger.cost_center`, `ledger.profit_center`.

**Edges.**
- Allocation must reconcile to 100 % of group capital. A residual unallocated bucket is permitted only for genuinely central items and must be disclosed.
- Allocation methodology changes are restatement events under `BR-DQ-009`.

**Control.** `CTL-019`, owner P-06. **Test.** `AC-058`. **Metric.** `MET-023`.

---

# Part D — Liquidity and Funding

## BR-LIQ-001 — Liquidity coverage ratio

**Statement.** LCR is the stock of unencumbered high quality liquid assets divided by total net cash outflows over a 30-calendar-day stress period, expressed as a percentage, at each required consolidation level and in each material currency.

**Source.** `treasury.liquidity_ratio` (`lcr_percentage`, `total_hqla_amount`, `hqla_level_1_amount`, `hqla_level_2a_amount`, `hqla_level_2b_amount`, `total_net_cash_outflow_amount`, `contractual_inflow_amount`, `retail_deposit_outflow_amount`, `secured_funding_outflow_amount`, `derivative_outflow_amount`, `committed_facility_outflow_amount`, `regulatory_threshold_percentage`, `consolidation_level`, `reporting_date`, `breach_flag`, `breach_severity`, `data_quality_score`), `risk.liquidity_metric`, `treasury.hqla_inventory`.

**Logic.**
```
hqla := hqla_level_1_amount
      + LEAST(hqla_level_2a_amount, 0.40 * total_hqla_amount)
      + LEAST(hqla_level_2b_amount, 0.15 * total_hqla_amount)
net_outflow := GREATEST(total_outflow - LEAST(total_inflow, 0.75 * total_outflow), 0)
lcr := hqla / net_outflow
```

**Edges.**
- Level 2 caps are applied after haircuts, in the order 2B then 2A. Applying them in the wrong order changes the answer.
- The 75 % inflow cap is applied at the currency and entity level at which the ratio is reported, not at group level then allocated.
- Encumbered assets are excluded entirely. `treasury.hqla_inventory` encumbrance status as at the close of the reporting date governs, not intra-day status.
- A `data_quality_score` below the `DC-012` threshold qualifies the ratio and the qualification is shown on `RPT-012`. A ratio published without its quality qualification is a control failure.

**Control.** `CTL-020`, owner P-04. **Test.** `AC-061`. **Metric.** `MET-005`.

---

## BR-LIQ-002 — Net stable funding ratio

**Statement.** NSFR is available stable funding divided by required stable funding, computed at each consolidation level, reported monthly and on demand.

**Source.** `treasury.liquidity_ratio` (`nsfr_percentage`, `available_stable_funding_amount`, `required_stable_funding_amount`), `risk.liquidity_metric` (`available_stable_funding_amount`, `required_stable_funding_amount`, `nsfr_ratio`, `nsfr_regulatory_minimum`).

**Edges.**
- ASF and RSF factors are applied by residual maturity bucket and counterparty type. A change in residual maturity across a bucket boundary changes the ratio without any transaction occurring; this effect must be identified separately in the monthly movement.

**Control.** `CTL-020`, owner P-04. **Test.** `AC-062`. **Metric.** `MET-006`.

---

## BR-LIQ-003 — Binding constraint identification

**Statement.** Every liquidity report must identify the binding constraint, which is the combination of legal entity, currency and consolidation level with the lowest headroom to its regulatory minimum. Reporting the group headline alone is insufficient.

**Source.** `treasury.liquidity_ratio` across all `consolidation_level` and `currency_id` combinations, `risk.liquidity_metric` (`liquidity_transfer_restriction`).

**Logic.** Headroom is `lcr_percentage - regulatory_threshold_percentage`. The binding constraint is the row with minimum headroom among rows whose `liquidity_transfer_restriction` prevents surplus from being moved to cover a deficit elsewhere.

**Edges.**
- A group in comfortable surplus can have a trapped-liquidity entity in breach. Any report that nets these together is wrong.
- Ring-fenced entities are never netted against the rest of the group.

**Control.** `CTL-020`, owner P-04. **Test.** `AC-063`.

---

## BR-LIQ-004 — Intraday liquidity monitoring

**Statement.** Intraday liquidity usage is measured continuously through the settlement day, capturing peak usage, available liquidity at peak, and the time of peak.

**Source.** `risk.liquidity_metric` (`intraday_available_liquidity_amount`, `intraday_peak_liquidity_amount`, `calculation_run_timestamp`), `treasury.nostro_account`, `payment.payment_transaction` (`settlement_timestamp`, `settlement_amount`, `settlement_status`).

**Edges.**
- Peak usage is a maximum over the day, not an end-of-day snapshot. An end-of-day measure that shows comfort while an intraday peak came within 5 % of available liquidity is a false assurance and is explicitly a failure of this rule.
- Throughput measured against the value-weighted settlement time distribution is reported, because delayed settlement is a liquidity risk indicator.

**Control.** `CTL-020`, owner P-04. **Test.** `AC-064`.

---

## BR-LIQ-005 — Survival horizon under stress

**Statement.** The survival horizon is the number of days until the cumulative net cash outflow under a stress scenario exhausts the counterbalancing capacity.

**Source.** `risk.liquidity_metric` (`survival_horizon_days`, `stress_scenario_id`), `treasury.cash_flow_forecast`, `treasury.contingency_funding_plan`, `treasury.stress_scenario_cfp`, `loan.facility_cfp_assumption`.

**Edges.**
- Behavioural assumptions on non-maturity deposits and on committed facility drawdown drive the answer more than contractual cash flows do. Each assumption must be traceable to `loan.facility_cfp_assumption` and must be model-validated under `BR-MDL-002`.
- A survival horizon computed with an unvalidated behavioural assumption is qualifying, not blocking, but must be labelled.

**Control.** `CTL-020`, owner P-04. **Test.** `AC-065`.

---

## BR-LIQ-006 — Funds transfer pricing

**Statement.** Every asset is charged and every liability is credited an internal funding rate reflecting tenor, liquidity premium, basis and optionality. FTP is a zero-sum allocation across the group, and the treasury residual is explicit.

**Source.** `treasury.ftp_rate` (`rate_code`, `composite_rate_bps`, `base_rate_value`, `liquidity_premium_bps`, `credit_spread_bps`, `basis_adjustment_bps`, `optionality_charge_bps`, `tenor_bucket`, `curve_type`, `asset_liability_flag`, `line_of_business`, `effective_date`, `expiration_date`, `rate_status`, `alco_approval_date`, `methodology`), `treasury.ftp_allocation`, `treasury.transfer_pricing_curve`.

**Logic.**
```
composite_rate_bps = base_rate_value
                   + liquidity_premium_bps
                   + credit_spread_bps
                   + basis_adjustment_bps
                   + optionality_charge_bps
```

**Edges.**
- A rate whose stored `composite_rate_bps` differs from the sum of its components is a blocking failure. FTP disputes with the business always start here.
- FTP charges and credits across all lines of business plus the treasury residual must sum to zero within USD 1,000. A non-zero sum means value is being created or destroyed by the allocation, which is impossible.
- A rate used outside its `effective_date` to `expiration_date` window is blocking.

**Control.** `CTL-021`, owner P-04. **Test.** `AC-066`. **Metric.** `MET-025`.

---

## BR-LIQ-007 — Nostro reconciliation

**Statement.** Every nostro account is reconciled daily against the correspondent's statement. Unmatched items are aged from the value date, not the discovery date.

**Source.** `treasury.nostro_account`, `treasury.nostro_reconciliation`, `payment.reconciliation`, `payment.payment_transaction` (`settlement_date`, `settlement_status`).

**Edges.**
- Ageing buckets are 0–1, 2–5, 6–30 and over 30 days. Any item over 30 days is escalated to P-06 and appears on the operational risk report as a potential loss event.
- A break that nets to zero across two accounts is still two breaks.

**Control.** `CTL-022`, owner P-04. **Test.** `AC-067`. **Metric.** `MET-038`.

---

# Part E — Market, Counterparty and Collateral Risk

## BR-MKT-001 — Value at risk and limit monitoring

**Statement.** VaR is computed daily per trading book at the confidence level and holding period specified on the governing limit, and is compared to that limit on the same basis.

**Source.** `risk.risk_limit` (`var_confidence_level`, `var_holding_period_days`, `amount`, `desk_code`, `limit_type`), `risk.market_risk_position`, `trade.trading_book`, `trade.mtm_valuation`, `trade.pnl_attribution`.

**Edges.**
- A VaR computed at 99 % over one day is never compared to a limit expressed at 97.5 % over ten days without explicit conversion, and the conversion method is recorded.
- Limit utilisation must use the same book hierarchy as the limit. Comparing desk-level VaR to a division-level limit is a defect.

**Control.** `CTL-023`, owner P-01. **Test.** `AC-071`.

---

## BR-MKT-002 — Backtesting exceptions

**Statement.** Daily clean profit and loss is compared to the prior day's VaR. An exception is a loss exceeding VaR. Exception counts drive the regulatory multiplier and are reported whether or not they breach.

**Source.** `trade.pnl_attribution`, `risk.market_risk_position`, `risk.model_validation` (`validation_outcome`), `risk.irb_model` (`backtesting_date`, `backtesting_result`).

**Edges.**
- Clean P&L excludes fees, commissions and intraday trading. Using dirty P&L understates exceptions.
- Four or more exceptions in 250 business days moves the model into the amber zone; ten or more into the red zone, which triggers `BR-MDL-005`.

**Control.** `CTL-023`, owner P-13. **Test.** `AC-072`.

---

## BR-MKT-003 — Counterparty credit exposure and valuation adjustments

**Statement.** Counterparty credit exposure for derivatives is measured as current exposure plus potential future exposure, net of enforceable netting and eligible collateral, with CVA, DVA and FVA measured and reported separately.

**Source.** `risk.credit_exposure` (`current_exposure`, `potential_future_exposure`, `expected_exposure`, `net_exposure`, `cva`, `dva`, `fva`, `cva_approach`, `cva_capital_charge`, `netting_set_id`, `collateral_value`), `collateral.netting_set`, `collateral.isda_master_agreement`, `collateral.csa_agreement`.

**Edges.**
- Netting applies only where a legally enforceable master agreement exists in the relevant jurisdiction, evidenced by `collateral.isda_master_agreement`. An assumed netting benefit without evidence is a blocking failure.
- CVA is reported gross. Netting CVA against DVA in management reporting is prohibited, because it obscures the counterparty risk position.
- Wrong-way risk, where exposure and counterparty credit quality are positively correlated, must be identified and separately reported.

**Control.** `CTL-024`, owner P-02. **Test.** `AC-073`.

---

## BR-MKT-004 — Settlement fails

**Statement.** A settlement fail is any trade not settled on its contractual settlement date. Fails are aged, valued and attributed to cause.

**Source.** `trade.settlement_instruction`, `trade.trade_lifecycle_event`, `payment.payment_transaction` (`settlement_status`, `settlement_date`, `failure_reason_code`).

**Edges.**
- A partial settlement is a fail for the unsettled portion.
- Fails caused by the counterparty and fails caused by OAFG are reported separately, because only one of them is an internal control issue.

**Control.** `CTL-024`, owner P-06. **Test.** `AC-074`. **Metric.** `MET-037`.

---

## BR-COL-001 — Collateral valuation currency and staleness

**Statement.** Collateral is valued at least as frequently as its asset class requires. A valuation older than the maximum age in `BR-IMP-007` is stale and is treated per that rule in every context, not only impairment.

**Source.** `collateral.collateral_valuation` (`valuation_date`, `valuation_amount`, `valuation_method`), `collateral.collateral_asset`, `collateral.stress_valuation`.

**Control.** `CTL-013`, owner P-02. **Test.** `AC-075`.

---

## BR-COL-002 — Margin call generation and ageing

**Statement.** A margin call arises when exposure net of posted collateral exceeds the threshold in the credit support annex by more than the minimum transfer amount. Calls are aged from issue, and unmet calls escalate.

**Source.** `collateral.collateral_margin_call`, `collateral.margin_agreement`, `collateral.csa_agreement`, `collateral.variation_margin`, `collateral.initial_margin`, `collateral.margin_exposure`.

**Edges.**
- Disputed calls are tracked separately from unmet calls. A dispute is not a default.
- A call unmet beyond the contractual cure period is a credit event and triggers watchlist entry under `BR-CRR-009`.

**Control.** `CTL-025`, owner P-02. **Test.** `AC-076`.

---

## BR-COL-003 — Collateral concentration and eligibility

**Statement.** Collateral eligibility is assessed per the eligibility rule set in force, and collateral concentration is measured as a dimension of `BR-CRR-005`. Ineligible collateral has zero value for risk mitigation and is still recorded.

**Source.** `collateral.eligibility_rule`, `collateral.concentration_limit`, `collateral.haircut_schedule`, `collateral.collateral_basket`, `security.instrument_eligibility`, `security.instrument_haircut_applicability`.

**Edges.**
- Collateral issued by the obligor or by an entity in the obligor's connected group is ineligible. This wrong-way collateral check is mandatory and is frequently missed.
- Concentration limits on collateral apply by issuer, by asset class and by currency simultaneously.

**Control.** `CTL-025`, owner P-02. **Test.** `AC-077`.

---

# Part F — Financial Crime

## BR-AML-001 — Customer risk rating

**Statement.** Every party carries a financial crime risk rating derived from country, product, channel, entity type, politically exposed person status, adverse media and transactional behaviour. The rating drives due diligence level and review frequency.

**Source.** `customer.party` (`risk_rating`, `is_pep`, `is_sanctioned`, `residency_status`, `citizenship_country_code`, `primary_address_country_code`, `customer_segment`), `customer.party_risk_rating`, `compliance.kyc_review` (`current_risk_rating`, `previous_risk_rating`, `due_diligence_level`, `risk_rating_change_reason`), `reference.country`, `reference.jurisdiction`.

**Logic.** Rating bands map to review frequency and due diligence level:

| Rating | Due diligence | Periodic review frequency | Approval to onboard |
|---|---|---|---|
| `low` | Simplified or standard | 60 months | Automated |
| `medium` | Standard | 36 months | Analyst |
| `high` | Enhanced | 12 months | Senior analyst |
| `prohibited` | None. Relationship refused or exited | n/a | Prohibited |

**Edges.**
- A PEP is never rated below high, irrespective of other factors.
- A rating downgrade from high to medium requires documented approval; upgrades to high are automatic on trigger.
- `is_sanctioned` true forces `prohibited` and triggers immediate escalation under `BR-AML-004`.

**Control.** `CTL-030`, owner P-07. **Test.** `AC-081`.

---

## BR-AML-002 — Periodic review currency

**Statement.** A KYC review is overdue when the current date exceeds `next_review_due_date`. Overdue high-risk customers are a regulatory exposure and are reported daily with ageing.

**Source.** `compliance.kyc_review` (`review_due_date`, `next_review_due_date`, `review_status`, `review_completed_date`, `review_approved_date`, `current_risk_rating`, `review_trigger_type`, `documentation_completeness_flag`, `outstanding_document_list`, `source_of_funds_verified`, `source_of_wealth_verified`, `beneficial_owner_identified`), `customer.party` (`kyc_status`, `kyc_next_review_date`).

**Edges.**
- A review that is complete but not approved is not complete. Both dates are required.
- An overdue review on a customer who is still transacting is escalated differently from one on a dormant customer, and the report must distinguish them.
- Overdue high-risk reviews beyond 90 days trigger a transaction restriction recommendation to P-07. The platform recommends; it never restricts.

**Control.** `CTL-030`, owner P-07. **Test.** `AC-082`. **Metric.** `MET-030`.

---

## BR-AML-003 — Beneficial ownership identification

**Statement.** For every non-individual customer, beneficial owners holding 25 % or more, and every controlling person regardless of holding, must be identified and verified. Ownership is traced through intermediate entities to natural persons.

**Source.** `customer.customer_beneficial_owner`, `customer.beneficial_owner`, `customer.corporate_profile`, `customer.relationship_hierarchy`, `compliance.kyc_review` (`beneficial_owner_identified`).

**Edges.**
- Where no natural person meets the 25 % threshold, senior managing officials are recorded instead. An empty beneficial owner record is never acceptable.
- Ownership chains must resolve to natural persons. A chain terminating in another entity is incomplete and is a qualifying failure.
- Nominee and trust structures require the settlor, trustee, protector and beneficiaries.

**Control.** `CTL-030`, owner P-07. **Test.** `AC-083`.

---

## BR-AML-004 — Sanctions screening

**Statement.** Parties, counterparties and payment messages are screened against applicable sanctions lists at onboarding, on list update, on payment initiation and periodically. A true match stops the activity.

**Source.** `compliance.sanctions_screening_event`, `compliance.sanctions_list_entry`, `payment.sanction_screening`, `payment.payment_transaction` (`sanctions_screening_status`), `customer.party` (`is_sanctioned`).

**Edges.**
- Screening is performed against the list version in force at screening time, and that version is recorded. Retrospective screening against a later list is a separate exercise and is reported separately.
- False positive rate is monitored by list and by matching algorithm. A false positive rate above 98 % on any list is an effectiveness concern reported to P-07, because it indicates the threshold is set so loosely that analysts stop reading.
- A payment released while its screening status is pending is a blocking control failure escalated same-day to P-07 and P-14.

**Control.** `CTL-031`, owner P-07. **Test.** `AC-084`. **Metric.** `MET-031`.

---

## BR-AML-005 — Alert generation, assignment and service level

**Statement.** Every alert has a deadline derived from its type and priority. Deadlines are measured in business hours from generation, and breaches are reported before they occur, not after.

**Source.** `compliance.aml_alert` (`alert_number`, `alert_type`, `alert_status`, `priority`, `detection_timestamp`, `assignment_date`, `review_start_timestamp`, `review_completion_timestamp`, `sla_deadline`, `disposition`, `closure_reason`, `closure_date`, `risk_score`, `escalation_reason`, `monitoring_rule_id`, `party_id`, `aml_case_id`).

**Service levels.**

| Priority | Triage | Disposition |
|---|---|---|
| Critical | 2 business hours | 3 business days |
| High | 8 business hours | 10 business days |
| Medium | 2 business days | 20 business days |
| Low | 5 business days | 30 business days |

**Edges.**
- An alert reassigned between analysts does not reset its deadline.
- An alert closed without a `closure_reason` is invalid and reopens automatically.
- Alerts pending because the customer has not responded are tracked in a distinct state, and that state has its own maximum duration.

**Control.** `CTL-032`, owner P-08. **Test.** `AC-085`.

---

## BR-AML-006 — Alert to case escalation

**Statement.** An alert escalates to a case when the analyst concludes that suspicion cannot be discounted. The case inherits the alert's subject and evidence and starts a new deadline governed by the filing obligation.

**Source.** `compliance.aml_alert` (`aml_case_id`, `escalation_reason`), `compliance.aml_case`, `fraud.case`, `fraud.evidence`.

**Edges.**
- Multiple alerts on the same subject within a lookback window merge into one case. A case that duplicates an open case on the same subject is a quality failure.
- Case closure without filing requires the same evidentiary standard as filing. "No further action" is a decision, and it is recorded as one.

**Control.** `CTL-032`, owner P-08. **Test.** `AC-086`. **Metric.** `MET-028`.

---

## BR-AML-007 — Suspicious activity report filing deadline

**Statement.** A SAR must be filed within the statutory deadline measured from the date of initial detection of facts constituting a basis for filing. The deadline is absolute and is tracked as a countdown, not a status.

**Source.** `compliance.aml_alert` (`sar_filed_flag`, `sar_filing_date`, `detection_date`), `fraud.sar_filing`, `compliance.ctr_filing`, `compliance.regulatory_calendar`.

**Deadlines.**

| Filing | Jurisdiction | Deadline |
|---|---|---|
| SAR | US | 30 calendar days from initial detection; 60 where no subject is identified |
| CTR | US | 15 calendar days from the transaction |
| Continuing activity SAR | US | 120 calendar days from the prior filing |
| STR | EU | Without delay, immediately on suspicion |

**Edges.**
- The clock starts at initial detection, which is the alert `detection_date`, not the escalation date and not the investigation start date. Starting it later is a compliance failure that the platform must make impossible to represent.
- A deadline falling on a non-business day does not extend.
- Continuing activity requires a further filing even where the original was filed and the case remains open.

**Control.** `CTL-033`, owner P-07. **Test.** `AC-087`. **Metric.** `MET-029`.

---

## BR-AML-008 — SAR confidentiality

**Statement.** The existence of a suspicious activity report, and the information that a report was considered, may be disclosed only to entitlement class `ENT-3` and to `ENT-6` under audit mandate. No other persona, report, extract, export or model feature may reveal or allow inference of it.

**Source.** `compliance.aml_alert` (`sar_filed_flag`, `sar_filing_date`), `fraud.sar_filing`, `fraud.fraud_alert` (`sar_filed_flag`, `sar_filing_date`).

**Implementation.** Column-level masking in Unity Catalog on every SAR-indicating column, plus row-level exclusion of `fraud.sar_filing` and the SAR-related subset of `compliance.aml_case` for all classes other than `ENT-3` and `ENT-6`.

**Edges.**
- Inference channels are in scope. A customer 360 view that hides `sar_filed_flag` but shows an unexplained account restriction whose only cause is a SAR still discloses it. Every derived field is assessed for inference risk under `CTL-011`.
- Aggregate counts of SARs are themselves restricted where the population is small enough to identify a subject. Minimum aggregation threshold is 20 subjects.
- This rule overrides every other reporting requirement in this document set without exception.

**Control.** `CTL-011`, owner P-07. **Test.** `AC-088`. **Severity.** Blocking, and a violation is a reportable regulatory incident.

---

## BR-AML-009 — Monitoring rule coverage and effectiveness

**Statement.** The monitoring rule inventory must demonstrably cover every typology in the risk assessment, across every product and channel. Coverage gaps and ineffective rules are both reported.

**Source.** `compliance.monitoring_rule`, `compliance.coverage`, `compliance.rule_validation`, `fraud.typology`, `compliance.aml_alert` (`monitoring_rule_id`, `disposition`).

**Logic.** For each rule: alerts generated, cases escalated, SARs filed, and the resulting precision. For each typology: whether at least one active, validated rule covers it in each product and channel combination.

**Edges.**
- A rule producing no true positives in six months is a tuning candidate, not automatically a retirement candidate, because a rare typology is still a covered typology. The report presents both facts and lets P-07 decide.
- A typology with no covering rule is a blocking coverage gap.
- Rule changes require pre-implementation testing against a historical population, and the test result is retained.

**Control.** `CTL-034`, owner P-07. **Test.** `AC-089`.

---

## BR-AML-010 — Transaction monitoring lookback

**Statement.** Where a monitoring rule is found to have been defective, a lookback is performed over the period of defect and any alerts that would have been generated are generated and worked.

**Source.** `compliance.monitoring_rule`, `compliance.rule_validation`, `compliance.aml_alert` (`lookback_period_days`, `model_version`).

**Edges.**
- Lookback alerts carry the original transaction dates but a current detection date for deadline purposes, and this must be explicit on the alert.
- A lookback is a reportable event to the supervisor in most jurisdictions and is tracked as a regulatory commitment on `RPT-021`.

**Control.** `CTL-034`, owner P-07. **Test.** `AC-090`.

---

# Part G — Fraud

## BR-FRD-001 — Fraud alert lifecycle and loss recognition

**Statement.** A fraud alert progresses through detection, triage, customer contact, disposition and, where loss occurs, recovery. Gross loss, recovery and net loss are distinct and are never conflated.

**Source.** `fraud.fraud_alert` (`alert_number`, `alert_status`, `score`, `severity`, `detection_method`, `generated_timestamp`, `review_started_timestamp`, `review_completed_timestamp`, `customer_contacted_flag`, `customer_contact_timestamp`, `customer_response`, `disposition_code`, `disposition_reason`, `false_positive_reason`, `loss_amount`, `recovery_amount`, `transaction_amount`, `transaction_channel`, `detection_rule_id`, `device_fingerprint_id`, `ip_address`, `geolocation_city`, `merchant_name`), `fraud.loss`, `fraud.loss_recovery`, `fraud.claim`.

**Logic.** `net_loss = loss_amount - recovery_amount`, never negative. Recovery exceeding loss indicates a data error and is blocking.

**Edges.**
- Loss is recognised in the period of the fraud event, and recovery in the period received. Reporting them in the same period distorts the loss rate trend.
- Losses reimbursed to the customer but recovered from a merchant or network are still OAFG losses until recovered.

**Control.** `CTL-035`, owner P-09. **Test.** `AC-091`. **Metric.** `MET-032`.

---

## BR-FRD-002 — Detection rule performance

**Statement.** Every detection rule is measured on volume, precision, recall proxy, value detected and value missed. A rule is tuned on evidence, never on intuition.

**Source.** `fraud.detection_rule`, `fraud.rule_performance`, `fraud.fraud_alert` (`detection_rule_id`, `disposition_code`), `fraud.fraud_incident`.

**Logic.**
```
precision := true_positive_alerts / total_alerts
value_detected := SUM(transaction_amount) WHERE disposition = confirmed_fraud AND prevented
value_missed := SUM(loss_amount) WHERE fraud confirmed AND no alert fired
```

**Edges.**
- Recall cannot be measured directly, because undetected fraud is unknown until reported. The proxy is fraud confirmed through customer report with no prior alert, which is `value_missed`.
- A rule change resets the performance baseline. Comparing performance across a rule version change without noting it is misleading and is prohibited on `RPT-025`.

**Control.** `CTL-035`, owner P-09. **Test.** `AC-092`. **Metric.** `MET-033`.

---

## BR-FRD-003 — Network and ring detection

**Statement.** Alerts are linked into networks by shared device fingerprint, IP address, contact details, beneficiary account, merchant or behavioural pattern. A network exceeding the linkage threshold becomes a fraud ring case.

**Source.** `fraud.network_link`, `fraud.fraud_ring`, `fraud.device_fingerprint`, `fraud.subject`, `fraud.subject_account_link`, `fraud.merchant`, `channel.session` (`device_fingerprint`, `ip_address`, `geolocation_country_code`).

**Edges.**
- Shared IP address alone is weak linkage, because of shared networks and carrier-grade address translation. Linkage strength is scored, and single-attribute links below the strength threshold do not create a ring.
- A ring spanning both fraud and AML subjects is escalated to both P-08 and P-09, and the two investigations are explicitly coordinated rather than duplicated.

**Control.** `CTL-035`, owner P-09. **Test.** `AC-093`.

---

## BR-FRD-004 — Chargeback management

**Statement.** Chargebacks are tracked against network deadlines by stage, and the merchant chargeback ratio is monitored against network thresholds.

**Source.** `fraud.chargeback`, `payment.card_transaction`, `payment.merchant`, `payment.merchant_agreement`, `fraud.merchant`.

**Edges.**
- Each network stage has its own deadline. A missed representment deadline is an automatic loss and is reported as an operational loss under `BR-ORX-001`.
- A merchant approaching a network monitoring threshold triggers commercial escalation before the threshold is crossed.

**Control.** `CTL-036`, owner P-09. **Test.** `AC-094`. **Metric.** `MET-034`.

---

# Part H — Payments and Channels

## BR-PAY-001 — Straight-through processing measurement

**Statement.** A payment is straight-through when it completes from initiation to settlement without manual intervention, repair or exception handling. Any touch disqualifies it.

**Source.** `payment.payment_transaction` (`settlement_status`, `failure_reason_code`, `return_reason_code`, `payment_type`, `payment_method`, `cross_border_flag`, `execution_timestamp`, `settlement_timestamp`), `payment.exception`, `payment.status_event`, `payment.instruction`.

**Edges.**
- Automated repair is still repair. It disqualifies the payment from STP but is reported separately from manual repair because the remediation differs.
- STP rate is reported by payment type, channel, currency and corridor. A single group STP number is not actionable.

**Control.** `CTL-037`, owner P-06. **Test.** `AC-101`. **Metric.** `MET-035`.

---

## BR-PAY-002 — Payment exception ageing and root cause

**Statement.** Every payment exception is aged from creation and attributed to a root cause category. Exceptions are worked to closure, and cause distribution drives remediation priority.

**Source.** `payment.exception`, `payment.payment_transaction` (`failure_reason_code`), `payment.return` (`return_reason_code`), `payment.status_event`.

**Edges.**
- An exception on a payment with a cut-off time is prioritised by time to cut-off, not by age.
- Repeated exceptions on the same beneficiary or the same corridor indicate a static-data problem, which is a data quality issue under `BR-DQ-006`, not a payments operations issue.

**Control.** `CTL-037`, owner P-06. **Test.** `AC-102`. **Metric.** `MET-036`.

---

## BR-PAY-003 — Payment screening completeness

**Statement.** Every cross-border payment and every payment involving a restricted party, currency or country must have a completed sanctions screening before release. Release without completed screening is a blocking control failure.

**Source.** `payment.payment_transaction` (`sanctions_screening_status`, `aml_screening_status`, `cross_border_flag`, `correspondent_bank_bic`, `intermediary_bank_bic`, `settlement_status`), `payment.sanction_screening`, `compliance.sanctions_screening_event`.

**Control.** `CTL-031`, owner P-07. **Test.** `AC-103`. **Severity.** Blocking.

---

## BR-CHN-001 — Channel availability and service level

**Statement.** Channel availability is measured against the published service level per channel, per region, in intervals of one minute, and is reported as both uptime percentage and customer-impacting minutes.

**Source.** `channel.channel`, `channel.digital_channel`, `channel.sla`, `channel.sla_breach`, `channel.channel_incident`, `channel.session` (`sla_compliance_flag`, `sla_actual_response_time_ms`, `sla_target_response_time_ms`, `session_status`, `outcome`).

**Edges.**
- Partial degradation counts. A channel responding in 12 seconds against a 2-second target is unavailable in customer terms even though it responds.
- Customer-impacting minutes weights downtime by the sessions that would have occurred, using the equivalent interval from the prior four weeks. Raw uptime percentage alone understates a peak-hour outage.

**Control.** `CTL-038`, owner P-10. **Test.** `AC-104`. **Metric.** `MET-044`.

---

## BR-CHN-002 — Journey completion and abandonment

**Statement.** Customer journeys are instrumented end to end with a defined start, defined completion and defined abandonment. Abandonment is attributed to the step at which it occurred.

**Source.** `channel.journey`, `channel.journey_instance`, `channel.journey_template`, `channel.session`, `channel.interaction`, `customer.onboarding_case`.

**Edges.**
- A journey resumed after abandonment on a different channel is one journey, not two. Cross-channel stitching uses `party_id`, and where the party is not yet identified it uses device fingerprint with a documented match confidence.
- Journey time excludes time waiting on the customer, and this exclusion must be visible, because operational improvement targets only the controllable portion.

**Control.** `CTL-038`, owner P-10. **Test.** `AC-105`. **Metric.** `MET-045`.

---

## BR-CHN-003 — Complaint capture and conduct signal

**Statement.** Every complaint is captured with product, channel, cause theme, resolution and outcome. Complaint themes are clustered and trended as a leading conduct risk indicator.

**Source.** `customer.complaint`, `channel.interaction`, `channel.channel_alert`, `compliance.breach`.

**Edges.**
- A complaint upheld against OAFG is a conduct signal even when the redress is immaterial. Materiality of redress is not materiality of signal.
- Complaint volume normalised by product holdings is the reportable measure. Raw counts favour small products.
- A theme growing more than 50 % quarter on quarter is escalated to P-07 and P-10 regardless of absolute volume.

**Control.** `CTL-039`, owner P-10. **Test.** `AC-106`. **Metric.** `MET-046`.

---

# Part I — Finance and Ledger

## BR-FIN-001 — Journal entry integrity

**Statement.** Every journal entry balances, in transaction currency and in functional currency, and carries a preparer, an approver who is a different person, and a source.

**Source.** `ledger.journal_entry` (`journal_number`, `total_debit_amount`, `total_credit_amount`, `functional_total_debit_amount`, `functional_total_credit_amount`, `preparer_name`, `approver_name`, `approval_status`, `approval_timestamp`, `posting_status`, `journal_source`, `journal_category`, `accounting_date`, `exchange_rate`, `intercompany_indicator`, `reversal_indicator`, `sox_control_reference`), `ledger.journal_entry_line`.

**Logic.** `total_debit_amount = total_credit_amount` and `functional_total_debit_amount = functional_total_credit_amount`, both exactly. `preparer_name <> approver_name`, always.

**Edges.**
- A self-approved journal is a blocking SOX control failure regardless of amount.
- Rounding differences on currency translation post to a designated translation account, never to a P&L line, and are separately reported.

**Control.** `CTL-040`, owner P-06. **Test.** `AC-111`. **Metric.** `MET-041`.

---

## BR-FIN-002 — Manual journal monitoring

**Statement.** Manual journals are monitored by volume, value, preparer, account and timing. Late-period manual journals above threshold receive enhanced scrutiny.

**Source.** `ledger.journal_entry` (`journal_source`, `journal_category`, `adjustment_indicator`, `posting_timestamp`, `accounting_date`), `ledger.accounting_period`.

**Edges.**
- A manual journal posted in the last two days of the close window and above USD 5 million requires controller approval and appears on `RPT-028` individually.
- Recurring manual journals indicate a process gap and are reported as such, with the count of consecutive periods.

**Control.** `CTL-040`, owner P-06. **Test.** `AC-112`.

---

## BR-FIN-003 — Subledger to general ledger reconciliation

**Statement.** Every subledger reconciles to its general ledger control account at every legal entity, every accounting period, in both transaction and functional currency.

**Source.** `ledger.subledger`, `ledger.subledger_reconciliation`, `ledger.gl_account`, `ledger.trial_balance`, `ledger.legal_entity`, `ledger.accounting_period`.

**Edges.**
- The reconciliation is performed at the control-account grain, not at the entity total. A netting of two offsetting breaks across accounts is not a reconciliation.
- Unreconciled differences below materiality still require an owner and an age. See `MAT-04`.
- A reconciliation signed off with an open material difference is a blocking control failure.

**Control.** `CTL-041`, owner P-06. **Test.** `AC-113`. **Metric.** `MET-040`.

---

## BR-FIN-004 — Financial close control tower

**Statement.** The close is a dependency graph of tasks, each with an owner, a due time, a predecessor set and a status. The critical path is computed and reported continuously through the close.

**Source.** `ledger.financial_close_task`, `ledger.task_template`, `ledger.accounting_calendar`, `ledger.consolidation_run`, `ledger.consolidation_group`.

**Edges.**
- A task cannot be marked complete while a predecessor is incomplete. Attempting it is a data integrity failure.
- The critical path is recomputed on every status change, not on a schedule, because the value of the report is knowing immediately when the path changes.
- Tasks that are late but off the critical path are reported distinctly from those that are late and on it.

**Control.** `CTL-042`, owner P-06. **Test.** `AC-114`. **Metric.** `MET-039`.

---

## BR-FIN-005 — Intercompany elimination

**Statement.** Intercompany balances and transactions eliminate fully on consolidation. Any residual after elimination is a mismatch requiring investigation, and is never absorbed into a consolidation adjustment.

**Source.** `ledger.intercompany_transaction`, `ledger.intercompany_elimination`, `ledger.consolidation_run`, `ledger.legal_entity`.

**Edges.**
- Timing differences across entity close calendars are the most common cause of residual and are identified as such rather than being posted away.
- Currency translation on intercompany balances creates genuine residual which posts to translation reserve, and this is the only permitted non-zero residual.

**Control.** `CTL-041`, owner P-06. **Test.** `AC-115`.

---

## BR-FIN-006 — Segment profitability

**Statement.** Segment results are reported after direct costs, allocated costs, FTP and allocated capital. Every allocation is traceable to its basis, and the sum of segments plus unallocated equals the group total exactly.

**Source.** `ledger.profit_center`, `ledger.cost_center`, `treasury.ftp_allocation`, `treasury.capital_ratio`, `ledger.journal_entry_line`, `ledger.gl_account`.

**Edges.**
- Allocation basis changes are restatement events. Prior periods are restated on the new basis and both bases are shown in the transition period.
- Unallocated must be genuinely central. An unallocated bucket exceeding 5 % of group cost is reported as an allocation quality issue.

**Control.** `CTL-019`, owner P-06. **Test.** `AC-116`. **Metric.** `MET-024`.

---

# Part J — Customer, Model Risk, Operational Risk and Audit

## BR-CUS-001 — Party golden record and deduplication

**Statement.** `customer.party` is the single source of party identity. A natural person or legal entity must appear exactly once. Duplicates are merged with a full audit trail and the surviving identifier is recorded on both records.

**Source.** `customer.party` (`party_id`, `cif_number`, `legal_name`, `date_of_birth`, `tax_identification_number`, `national_id_number`, `lei_registry_id`, `duns_number`, `source_system_code`, `lifecycle_status`), `customer.party_identifier`, `customer.party_lifecycle_event`.

**Edges.**
- A merge is never a delete. Both records persist, with the non-surviving record marked `merged` in `lifecycle_status` and pointing to the survivor.
- Historical reporting for periods before a merge must reproduce the pre-merge position. This is a bitemporal requirement, not an optional nicety.
- Suspected duplicates that have not been merged are reported on `RPT-038` with a confidence score. Automatic merging without human confirmation is prohibited.

**Control.** `CTL-043`, owner P-12. **Test.** `AC-121`.

---

## BR-CUS-002 — Relationship manager assignment and access scope

**Statement.** A relationship manager's data access is derived from their recorded client and account assignments, and from nothing else.

**Source.** `channel.rm_client_assignment`, `channel.channel_relationship_manager`, `account.rm_account_assignment`, `customer.customer_relationship_manager`, `wealth.portfolio_assignment`, `hr.employee`.

**Edges.**
- Assignment changes take effect at the next entitlement refresh, which is at most 15 minutes. A departing employee's access is revoked immediately on HR termination, not at the next refresh.
- Team-based coverage grants access to the team's aggregate portfolio, and this is an explicit assignment type, not an implicit inheritance.

**Control.** `CTL-003`, owner P-12. **Test.** `AC-122`.

---

## BR-CUS-003 — Consent and data subject rights

**Statement.** Marketing use, profiling and cross-entity data sharing require a recorded, current, purpose-specific consent. A data subject access, rectification or erasure request is tracked to a statutory deadline.

**Source.** `customer.consent_record`, `compliance.data_subject_request`, `customer.marketing_campaign`, `channel.campaign`.

**Edges.**
- Withdrawal of consent is effective immediately and propagates to every downstream consumer within one pipeline cycle.
- Erasure is constrained by regulatory retention obligations. Where they conflict, retention wins and the constraint is recorded and communicated. Silent non-erasure is prohibited.
- Consent for one purpose never implies consent for another.

**Control.** `CTL-014`, owner P-12. **Test.** `AC-123`.

---

## BR-MDL-001 — Model inventory completeness

**Statement.** Every model whose output influences a financial statement, a regulatory submission, a customer decision or a risk limit is in the inventory, with an owner, a validation status and a recorded dependency on the metrics it feeds.

**Source.** `risk.irb_model`, `risk.valuation_model`, `risk.model_validation`, `risk.model_deployment`, `fraud.detection_rule`, `compliance.monitoring_rule`, `wealth.suitability_assessment`.

**Edges.**
- Rules and scorecards are models for this purpose. A fraud detection rule and an AML monitoring rule are both in the inventory.
- The boundary with `ASM-04` is: the platform records model metadata, versions, performance and dependencies. It does not calibrate models. A model calculated inside a report is by definition an undocumented model and is a blocking failure.

**Control.** `CTL-018`, owner P-13. **Test.** `AC-131`.

---

## BR-MDL-002 — Validation currency

**Statement.** A model's validation is current when the last validation is within the frequency set by its model risk rating. Overdue validation is escalated before the due date, not after.

**Source.** `risk.irb_model` (`last_validation_date`, `next_validation_date`, `model_risk_rating`, `validation_outcome`), `risk.model_validation`.

| Model risk rating | Validation frequency | Escalation lead time |
|---|---|---|
| High | 12 months | 90 days |
| Medium | 24 months | 60 days |
| Low | 36 months | 60 days |

**Control.** `CTL-018`, owner P-13. **Test.** `AC-132`. **Metric.** `MET-047`.

---

## BR-MDL-003 — Performance monitoring thresholds

**Statement.** Live model performance is monitored against thresholds set at validation. Breach of a threshold triggers review, and breach on a model feeding a regulatory number triggers immediate notification.

**Source.** `risk.irb_model` (`gini_coefficient`, `auc_roc`, `brier_score`, `backtesting_result`, `backtesting_date`, `override_rate`, `long_run_average_pd`), `fraud.rule_performance`, `compliance.rule_validation`.

**Edges.**
- Degradation is measured against the validation baseline, not against the prior period. Slow drift passes a period-on-period test and fails a baseline test.
- Population stability is monitored alongside discrimination. A model with stable Gini on a shifted population is not stable.

**Control.** `CTL-018`, owner P-13. **Test.** `AC-133`.

---

## BR-MDL-004 — Unapproved model use

**Statement.** Use of a model outside its approval, whether by asset class, entity, purpose or date range, is a blocking failure. The affected calculation falls back to the approved alternative and the fallback is reported.

**Source.** `risk.irb_model` (`regulatory_approval_status`, `asset_class`, `use_in_rwa_calculation`, `use_in_ecl_calculation`, `effective_from_date`, `effective_until_date`), `risk.model_deployment`.

**Control.** `CTL-018`, owner P-13. **Test.** `AC-134`. **Severity.** Blocking.

---

## BR-MDL-005 — Model to metric dependency

**Statement.** Every certified metric records the models it depends on. The dependency is queryable in both directions, so that a model failure immediately identifies the affected metrics and reports.

**Source.** `risk.irb_model`, `risk.model_deployment`, plus the Gold-layer metric registry defined in [05](./05-semantic-layer-and-metrics.md).

**Edges.**
- A metric whose model dependency is unrecorded cannot be certified. This is the enforcement mechanism, not a documentation aspiration.
- Dependency is transitive: a metric depending on another metric inherits its model dependencies.

**Control.** `CTL-018`, owner P-13 and P-12 jointly. **Test.** `AC-135`.

---

## BR-ORX-001 — Operational risk event capture

**Statement.** Every operational risk event is captured with gross loss, recoveries, insurance recoveries, net loss, Basel event type, business line, causal factor and root cause. Near misses are captured with the same rigour.

**Source.** `risk.operational_risk_event` (`event_reference_number`, `event_date`, `discovery_date`, `accounting_date`, `gross_loss_amount`, `recovery_amount`, `insurance_recovery_amount`, `net_loss_amount`, `legal_provision_amount`, `basel_event_type_category`, `basel_event_type_level2`, `business_line_code`, `causal_factor_code`, `root_cause_category`, `near_miss_indicator`, `regulatory_reportable_indicator`, `loss_threshold_met_indicator`, `corrective_action_status`, `corrective_action_due_date`, `event_status`).

**Edges.**
- Event date, discovery date and accounting date are three different dates and all three are required. Loss trending on the wrong one produces the wrong conclusion.
- A single root cause producing multiple losses is one event with multiple loss records, not multiple events.
- Boundary events, which are credit or market losses caused by an operational failure, are recorded in both places and flagged so that they are not double counted in aggregate loss.

**Control.** `CTL-044`, owner P-01. **Test.** `AC-136`. **Metric.** `MET-026`.

---

## BR-ORX-002 — Key risk indicator thresholds

**Statement.** Every KRI has green, amber and red thresholds, a direction, an owner, a measurement frequency and an escalation authority. A KRI without all six is not a KRI.

**Source.** `risk.kri_measurement` (`kri_code`, `kri_name`, `actual_value`, `green_threshold`, `amber_threshold`, `red_threshold`, `threshold_direction`, `kri_owner_name`, `kri_owner_role`, `measurement_frequency`, `escalation_authority`, `escalation_status`, `breach_status`, `remediation_action`, `remediation_due_date`, `is_board_reported`, `is_regulatory_kri`, `data_quality_flag`, `data_quality_score`).

**Edges.**
- A KRI with a `data_quality_flag` indicating a problem is reported with the flag visible. A red KRI on bad data and a red KRI on good data require different responses.
- Trend matters as much as level. Three consecutive periods of deterioration inside the green band is a reportable trend.

**Control.** `CTL-044`, owner P-01. **Test.** `AC-137`. **Metric.** `MET-027`.

---

## BR-AUD-001 — Finding and management action tracking

**Statement.** Every audit finding has a rating, an owner, an agreed action, a due date and a validation step. Closure requires audit validation, not management assertion.

**Source.** `audit.finding`, `audit.recommendation`, `audit.management_action`, `audit.issue_validation`, `audit.issue_tracker`, `compliance.exam_finding`, `compliance.regulatory_exam`.

**Edges.**
- A due date extension is itself an event requiring approval at a level determined by the finding's rating, and extensions are counted and reported. A finding extended three times is reported to the Audit Committee irrespective of its rating.
- Regulatory findings and internal findings are tracked in the same framework but never merged in reporting, because their escalation paths differ.
- A closed finding whose root cause recurs reopens as a repeat finding, and repeat findings are rated at least one level higher.

**Control.** `CTL-045`, owner P-14. **Test.** `AC-141`. **Metric.** `MET-049`.

---

## BR-AUD-002 — Three lines assignment

**Statement.** Every control has an assigned line of defence. A control performed and monitored by the same team is not a control, and is reported as a segregation gap.

**Source.** `audit.three_lines_assignment`, `audit.business_process`, `ledger.ledger_sox_control`, `compliance.compliance_sox_control`.

**Control.** `CTL-045`, owner P-14. **Test.** `AC-142`.

---

# Part K — Data Quality

## BR-DQ-001 — Critical data element designation

**Statement.** An attribute is a critical data element when its failure would materially misstate a board-reported metric or a regulatory submission, or would cause an incorrect customer outcome. Every CDE has a named steward, a quality rule set and a measured score.

**Source.** All `banking_ecm` schemas. The CDE register is a Gold-layer asset defined in [06](./06-governance-security-and-controls.md).

**Edges.**
- CDE designation is derived from metric lineage, not asserted. Any column feeding a board-reported or regulatory-submitted metric is automatically a CDE candidate and must be either designated or explicitly excluded with a reason.
- A CDE with no steward is a blocking governance failure and appears on `RPT-038` daily until resolved.

**Control.** `CTL-050`, owner P-12. **Test.** `AC-151`. **Metric.** `MET-050`.

---

## BR-DQ-002 — Referential integrity

**Statement.** Every foreign key value in `banking_ecm` must resolve to an existing parent row. The model declares 3,301 foreign keys; all are enforced logically at Silver load whether or not the platform enforces them physically.

**Logic.** For each declared FK, count of child rows whose key does not resolve. Threshold zero.

**Edges.**
- Nullable foreign keys are permitted where the model declares them nullable. A null is not an orphan.
- An orphan on a CDE-bearing relationship is blocking. An orphan elsewhere is qualifying.
- Orphans are never resolved by creating a placeholder parent. That converts a visible failure into an invisible one.

**Control.** `CTL-050`, owner P-12. **Test.** `AC-152`. **Severity.** Blocking for CDE relationships.

---

## BR-DQ-003 — Hierarchy integrity

**Statement.** Party relationship hierarchies, chart of accounts hierarchies and organisational hierarchies must be acyclic, fully connected to a root, and within the declared maximum depth.

**Source.** `customer.relationship_hierarchy`, `ledger.chart_of_accounts`, `hr.org_unit`, `ledger.consolidation_group`.

**Control.** `CTL-050`, owner P-12. **Test.** `AC-153`. **Severity.** Blocking.

---

## BR-DQ-004 — Cross-system agreement

**Statement.** Where the same business fact exists in two domains, the two must agree within tolerance. Disagreement is a finding against the source systems, not a reason to pick one.

**Reconciliation set.**

| # | Fact | Source A | Source B | Tolerance |
|---|---|---|---|---|
| 1 | Loan outstanding balance | `loan.loan_account.outstanding_principal_balance` | `ledger` control account | USD 1 per account |
| 2 | ECL provision | `risk.risk_ecl_provision.provision_amount` | `loan.loan_ecl_provision` | Zero |
| 3 | Credit exposure | `risk.credit_exposure.ead` | `loan.facility` drawn plus converted undrawn | 0.1 % |
| 4 | Capital ratio inputs | `treasury.capital_ratio.credit_rwa_amount` | `SUM(risk.credit_exposure.rwa_credit)` | 0.05 % |
| 5 | Deposit balance | `account.deposit_account` balance | `ledger` control account | USD 1 per account |
| 6 | Payment settlement | `payment.payment_transaction.settlement_amount` | `treasury.nostro_reconciliation` | Zero |
| 7 | Party count | `customer.party` active | CRM active client count | 0.01 % |
| 8 | Collateral value | `collateral.collateral_valuation.valuation_amount` | `risk.credit_exposure.collateral_value` | 0.5 % |
| 9 | Fraud loss | `fraud.loss` | `risk.operational_risk_event.gross_loss_amount` | Zero for events above threshold |
| 10 | Rating | `risk.counterparty_rating.rating_code` | `customer.party_risk_rating.internal_rating_grade` | Exact match |

**Control.** `CTL-051`, owner P-12. **Test.** `AC-154`.

---

## BR-DQ-005 — Type and domain conformance

**Statement.** Every column conforms to its declared type, its declared valid value set and its declared pattern. The ECM model states valid values in column comments; those statements are enforceable rules.

**Examples of enforced domains.**

| Column | Rule |
|---|---|
| `customer.party.kyc_status` | One of `pending`, `verified`, `expired`, `rejected` |
| `customer.party.risk_rating` | One of `low`, `medium`, `high`, `prohibited` |
| `customer.party.lifecycle_status` | One of `prospect`, `active`, `dormant`, `deceased`, `closed`, `merged` |
| `customer.party.customer_segment` | One of `retail`, `corporate`, `institutional`, `government`, `private_wealth` |
| `customer.party.citizenship_country_code` | Matches `^[A-Z]{3}$` and exists in `reference.country` |
| `customer.party.residency_status` | One of `resident`, `non_resident`, `dual_resident` |
| `loan.loan_account.days_past_due` | Stored as `STRING`; must cast to a non-negative integer |
| `risk.risk_ecl_provision.ifrs9_stage` | One of `1`, `2`, `3`, `POCI` |

**Edges.**
- Several ECM columns that are semantically numeric are typed `STRING` (`days_past_due`, `override_count`, `survival_horizon_days`, `transaction_count`, `stress_horizon_quarters`, `number_of_rating_grades`). Every consumer casts defensively and a failed cast is a blocking failure, never a silent null.
- A new value appearing in a constrained domain is a blocking failure, not an automatic domain extension.

**Control.** `CTL-050`, owner P-12. **Test.** `AC-155`.

---

## BR-DQ-006 — Completeness by criticality

**Statement.** Completeness thresholds vary by criticality. A CDE has a stricter threshold than a descriptive attribute, and thresholds are set per column, not per table.

| Criticality | Null tolerance | Violation severity |
|---|---|---|
| Regulatory-submitted CDE | 0.00 % | Blocking |
| Board-reported CDE | 0.01 % | Blocking |
| Management-reported | 0.50 % | Qualifying |
| Descriptive | 5.00 % | Advisory |

**Control.** `CTL-050`, owner P-12. **Test.** `AC-156`.

---

## BR-DQ-007 — Single definition enforcement

**Statement.** A certified metric is computed in exactly one place. Any second implementation, in any tool, is a defect regardless of whether it produces the same answer.

**Detection.** Static analysis of deployed SQL and semantic model definitions for calculations matching a certified metric's pattern outside the certified view. Detection runs weekly and reports to P-12.

**Control.** `CTL-052`, owner P-12. **Test.** `AC-157`.

---

## BR-DQ-008 — Timeliness and freshness

**Statement.** Every dataset has a maximum acceptable age relative to its `as_of_date`, defined in [04](./04-data-contracts-and-slos.md). A report consuming stale data displays the staleness prominently and, where the data is regulatory, does not publish.

**Control.** `CTL-053`, owner P-12. **Test.** `AC-158`.

---

## BR-DQ-009 — Restatement policy

**Statement.** A change to a previously published or submitted figure is a restatement. Restatements are classified, quantified, approved and disclosed. They are never made silently.

**Classification.**

| Class | Definition | Approval | Disclosure |
|---|---|---|---|
| R1 Error correction | The prior figure was wrong | P-05 and P-06; P-01 where risk | Prior period restated and disclosed |
| R2 Methodology change | Definition or allocation basis changed | Metric owner, P-12, and the relevant executive | Both bases shown in the transition period |
| R3 Late data | Correct method, data arrived after publication | P-05 | Disclosed if material, prospective if not |
| R4 Model change | New or recalibrated model | P-13 and the metric owner | Impact quantified and disclosed |

**Edges.**
- Every restatement quantifies the effect on each affected published figure, per period.
- A restatement of a regulatory submission triggers the supervisor notification process, which is a commitment tracked on `RPT-021` for financial crime and `RPT-009` otherwise.
- Frozen submission snapshots are never edited. A restatement creates a new snapshot with a new version and the original remains available. This is `ARCH-05` restated as a business rule.

**Control.** `CTL-054`, owner P-12. **Test.** `AC-159`. **Severity.** Blocking if a restatement is made without classification.

---

## BR-DQ-010 — Reconciliation before publication

**Statement.** No report publishes before its reconciliation set has run and either passed or been explicitly qualified by a named approver.

**Control.** `CTL-051`, owner P-12. **Test.** `AC-160`.

---

## BR-DQ-011 — Currency translation verification

**Statement.** Every stored translated amount is verified against a recomputation using the stored rate. Divergence beyond 1 basis point is a qualifying failure.

**Source.** `risk.credit_exposure` (`fx_rate`, `reporting_currency_code`), `risk.concentration_risk` (`fx_rate`, `exposure_reporting_currency`), `payment.payment_transaction` (`exchange_rate`, `settlement_amount`, `amount`), `ledger.journal_entry` (`exchange_rate`), `reference.exchange_rate`.

**Control.** `CTL-055`, owner P-12. **Test.** `AC-161`.

---

## BR-DQ-012 — Late-arriving data

**Statement.** Data arriving after its contract deadline is processed on arrival, not held to the next cycle. The affected reports are recomputed and any already-published figure is assessed for restatement under `BR-DQ-009`.

**Handling by report class.**

| Report class | Behaviour on late arrival |
|---|---|
| Daily regulatory (LCR, FR 2052a) | Publish at the deadline with the qualification banner and the known gap quantified. Recompute and reissue on arrival. Never delay the deadline. |
| Monthly management | Delay up to 4 hours, then publish qualified |
| Regulatory submission | Do not submit. Escalate to P-05 for a filing extension decision |
| Operational (fraud, AML, payments) | Publish immediately with the gap visible, because operational decisions cannot wait |

**Edges.**
- "Publish with the gap quantified" means naming the missing feed and the population it would have contributed, not a generic warning.
- A feed late more than three times in a rolling quarter is a data contract breach under [04](./04-data-contracts-and-slos.md) and is escalated to the source system owner.

**Control.** `CTL-053`, owner P-12. **Test.** `AC-162`.

---

## BR-DQ-013 — Quality score construction

**Statement.** A dataset's quality score is the weighted proportion of its quality rules passing, weighted by rule criticality. The score is published with every report that consumes the dataset.

**Logic.**
```
score := SUM(rule_weight * CASE WHEN rule_passed THEN 1 ELSE 0 END) / SUM(rule_weight)
```
Weights: blocking rules 5, qualifying 3, advisory 1. A score is never above 0.80 while any blocking rule fails, regardless of arithmetic.

**Control.** `CTL-050`, owner P-12. **Test.** `AC-163`. **Metric.** `MET-050`.

---

# Part L — Regulatory Reporting

## BR-REG-001 — Submission population lock

**Statement.** The population for a regulatory submission is locked at a defined cut-off. Records arriving after the cut-off do not enter the submission; they enter the next period and are identified as prior-period arrivals.

**Control.** `CTL-060`, owner P-05. **Test.** `AC-171`.

---

## BR-REG-002 — Validation rules before submission

**Statement.** Every supervisor-published validation rule is executed before submission. A failure is either corrected or explained with a recorded rationale and an approver. A submission with unexplained failures is prohibited.

**Source.** `compliance.compliance_regulatory_filing`, `compliance.regulatory_calendar`, `compliance.rule_validation`, `risk.risk_report`.

**Control.** `CTL-060`, owner P-05. **Test.** `AC-172`.

---

## BR-REG-003 — Return to ledger reconciliation

**Statement.** Every financial return reconciles to the general ledger. The bridge is produced as part of the submission pack and is retained with it.

**Control.** `CTL-060`, owner P-05. **Test.** `AC-173`.

---

## BR-REG-004 — Frozen submission snapshot

**Statement.** At submission, the complete input population, the derived output, the parameters, the model versions, the FX rates and the code version are frozen as an immutable snapshot, addressable by submission reference for the full retention period.

**Source.** `compliance.compliance_regulatory_filing` (`submission_reference`), `risk.stress_test_run` (`submission_reference`, `submission_date`), `treasury.capital_ratio` (`regulatory_submission_flag`, `submission_date`), `treasury.liquidity_ratio` (`regulatory_submission_flag`, `submission_date`).

**Edges.**
- The snapshot must be reproducible bit for bit. A reproduction that differs is a severity-1 defect.
- Retention is the longer of the supervisory requirement and ten years.
- Access to snapshots is read-only for everyone, including the platform team. There is no privileged path to edit one.

**Control.** `CTL-061`, owner P-05. **Test.** `AC-174`. **Severity.** Blocking.

---

## BR-REG-005 — AnaCredit loan-level population

**Statement.** The AnaCredit population is every credit exposure to a legal entity above the reporting threshold, at loan level, with counterparty reference data, protection received and accounting data.

**Source.** `loan.loan_account`, `loan.facility`, `customer.party`, `customer.corporate_profile`, `collateral.collateral_pledge`, `collateral.collateral_asset`, `risk.risk_ecl_provision`, `reference.country`, `reference.lei_registry`, `reference.industry_code`.

**Edges.**
- Counterparty reference data must be complete for every counterparty in the population, including protection providers who are not otherwise OAFG customers. This is the most common gap and is tested explicitly.
- Threshold application is at the obligor level across all instruments, not per instrument.
- Population movements between months are explained: new, matured, repaid, transferred, threshold entry and threshold exit.

**Control.** `CTL-060`, owner P-05. **Test.** `AC-175`.

---

## BR-REG-006 — FR Y-14 loan-level population

**Statement.** FR Y-14Q and Y-14M loan-level schedules are produced at the required grain with the required attributes, sourced from the same certified layer as management reporting.

**Edges.**
- Any attribute required by the schedule that does not exist in `banking_ecm` is a gap raised against the data model, never filled by a report-level derivation.
- The submitted population must reconcile to the Y-9C balance sheet.

**Control.** `CTL-060`, owner P-05. **Test.** `AC-176`.

---

## BR-REG-007 — Pillar 3 disclosure consistency

**Statement.** Publicly disclosed risk figures must equal the corresponding supervisory submission figures for the same date and basis. Any difference requires an explicit, disclosed reconciling item.

**Source.** `risk.credit_exposure` (`pillar3_disclosure_flag`), `treasury.capital_ratio`, `risk.risk_report`.

**Control.** `CTL-060`, owner P-05. **Test.** `AC-177`.

---

## BR-REG-008 — Supervisory ad-hoc request service level

**Statement.** An ad-hoc supervisory data request is fulfilled from the certified layer within four hours for aggregations already supported by the semantic layer, and within two business days otherwise. This is programme objective O3.

**Edges.**
- A request that cannot be met from the certified layer is a capability gap and is logged, because the pattern of gaps drives the semantic layer roadmap.
- Ad-hoc responses are versioned and retained exactly as submissions are, under `BR-REG-004`.

**Control.** `CTL-061`, owner P-05. **Test.** `AC-178`.

---

## Appendix A — Rule index by domain

| Domain | Prefix | Rules | Owning persona |
|---|---|---|---|
| Credit risk | `BR-CRR` | 001–014 | P-02 |
| Impairment | `BR-IMP` | 001–012 | P-02 with P-06 |
| Capital | `BR-CAP` | 001–008 | P-04 |
| Liquidity and funding | `BR-LIQ` | 001–007 | P-04 |
| Market and counterparty | `BR-MKT` | 001–004 | P-01 |
| Collateral | `BR-COL` | 001–003 | P-02 |
| Financial crime | `BR-AML` | 001–010 | P-07 |
| Fraud | `BR-FRD` | 001–004 | P-09 |
| Payments | `BR-PAY` | 001–003 | P-06 |
| Channels | `BR-CHN` | 001–003 | P-10 |
| Finance and ledger | `BR-FIN` | 001–006 | P-06 |
| Customer | `BR-CUS` | 001–003 | P-12 |
| Model risk | `BR-MDL` | 001–005 | P-13 |
| Operational risk | `BR-ORX` | 001–002 | P-01 |
| Audit | `BR-AUD` | 001–002 | P-14 |
| Data quality | `BR-DQ` | 001–013 | P-12 |
| Regulatory reporting | `BR-REG` | 001–008 | P-05 |

## Appendix B — Blocking rules

These rules stop a publication or a submission. There is no override path that does not involve a named executive accepting the risk in writing.

`BR-CRR-001` orphan party · `BR-CRR-004` missing capital base · `BR-CRR-006` unapproved IRB CCF · `BR-CRR-011` expired limit with exposure · `BR-CRR-012` appetite metric without threshold · `BR-CRR-014` drawn facility behind uncleared application · `BR-IMP-003` stage 3 to NPL mismatch · `BR-IMP-004` POCI with numeric stage · `BR-IMP-005` scenario weights not summing to one · `BR-IMP-005` unapproved overlay · `BR-IMP-009` non-zero attribution residual · `BR-IMP-010` unposted provision at close · `BR-IMP-012` write-off without provision release · `BR-CAP-001` ratio divergence beyond 1 bp · `BR-CAP-004` missing standardised parallel run · `BR-CAP-006` incomplete stress run reported as result · `BR-LIQ-006` FTP allocation not summing to zero · `BR-AML-004` payment released on pending screening · `BR-AML-008` SAR confidentiality breach · `BR-AML-009` uncovered typology · `BR-PAY-003` unscreened cross-border payment · `BR-FIN-001` self-approved journal · `BR-FIN-003` sign-off with open material difference · `BR-MDL-001` model calculated inside a report · `BR-MDL-004` unapproved model use · `BR-DQ-002` orphan on a CDE relationship · `BR-DQ-003` hierarchy cycle · `BR-DQ-005` failed cast on a CDE · `BR-DQ-006` completeness breach on a regulatory CDE · `BR-DQ-009` unclassified restatement · `BR-REG-004` non-reproducible submission snapshot.
