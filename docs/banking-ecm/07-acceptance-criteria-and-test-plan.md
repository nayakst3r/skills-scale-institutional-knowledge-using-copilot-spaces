# 07 — Acceptance Criteria and Test Plan

**Document ID:** OAFG-BSR-2026-07 · **Version:** 1.0 · **Owner:** Head of Quality Assurance · **Approvers:** each owning persona

---

## 1. Acceptance principles

| Principle | Statement |
|---|---|
| `TP-01` | A requirement is done when its acceptance criterion passes on production-shaped data, not when the code merges |
| `TP-02` | Every acceptance criterion is automated and runs on every build. A criterion that only a person can check is rewritten until a machine can |
| `TP-03` | Negative cases carry equal weight. A rule that fires correctly but also fires when it should not has failed |
| `TP-04` | Reconciliation tests use independently derived expected values. Comparing the platform to itself proves nothing |
| `TP-05` | An entitlement criterion is proven by attempted access from every class, not by inspecting the policy |
| `TP-06` | Reproducibility criteria run against a snapshot taken at least one full cycle earlier, so that "reproducible" means across time, not within a run |
| `TP-07` | Performance criteria run at the volumetrics in [00, section 1.3](./00-programme-charter-and-scope.md#13-scale-assumptions), not at test-data scale |

## 2. Test levels

| Level | What it proves | Gate |
|---|---|---|
| L1 Contract | The source delivered what it agreed to | Blocks promotion to Silver |
| L2 Rule | A business rule computes correctly, including its edges | Blocks promotion to Gold |
| L3 Metric | A certified metric matches its definition and its dimensional behaviour | Blocks certification |
| L4 Report | A report meets its grain, content, latency and entitlement specification | Blocks publication |
| L5 Reconciliation | Independent views agree within tolerance | Blocks sign-off and submission |
| L6 Non-functional | Latency, concurrency, availability and recovery hold at scale | Blocks release |
| L7 User acceptance | The owning persona confirms the report answers their stated questions | Blocks go-live |

---

## 3. Detailed criteria for the hard requirements

The criteria below are written out in full because they are the ones most likely to be implemented incorrectly. Section 4 indexes every remaining criterion.

### AC-013 — Connected client group traversal

```gherkin
Feature: Connected client group aggregation (BR-CRR-003)

  Scenario: Transitive control chain resolves to the ultimate parent
    Given party A controls party B
      And party B controls party C
      And party C has no controlled subsidiaries
     When the connected client group is derived for as_of_date 2026-06-30
     Then parties A, B and C belong to one group whose identifier is A
      And the group aggregate EAD equals the sum of the EAD of A, B and C

  Scenario: Joint control assigns to both groups with disclosed double count
    Given party X is controlled 50 percent by party P and 50 percent by party Q
     When the connected client group is derived
     Then X belongs to group P and to group Q
      And X's full EAD counts against both group limits
      And the group total counts X once, using the greater group assignment
      And the double-counted amount appears as a disclosed reconciling line on RPT-003

  Scenario: Depth beyond the maximum is blocking, never truncated
    Given a control chain of 13 levels exists in the data
     When the connected client group is derived
     Then a blocking failure is raised
      And no group is produced with a silently truncated membership

  Scenario: Economic dependency is included only when recorded
    Given party S is a supplier whose failure would cause party B to fail
      And no credit analyst has recorded that dependency
     When the connected client group is derived
     Then S is not a member of B's group

  Scenario: A cycle in the data blocks rather than loops
    Given party A controls party B and party B controls party A in the source data
     When the connected client group is derived
     Then a blocking failure is raised under BR-DQ-003
      And the derivation terminates rather than iterating
```

### AC-032 — Significant increase in credit risk

```gherkin
Feature: Stage 1 to stage 2 transfer (BR-IMP-002)

  Scenario Outline: The quantitative test requires both relative and absolute triggers
    Given an exposure in segment "<segment>"
      And a lifetime PD at origination of <pd_orig>
      And a lifetime PD at reporting date of <pd_now>
     When the SICR test runs
     Then the quantitative trigger is "<result>"

    Examples:
      | segment                      | pd_orig | pd_now | result   |
      | corporate_investment_grade   | 0.0020  | 0.0055 | fired    |
      | corporate_investment_grade   | 0.0020  | 0.0045 | not fired|
      | retail_unsecured             | 0.0400  | 0.0640 | not fired|
      | retail_unsecured             | 0.0400  | 0.0800 | fired    |
      | sovereign_and_bank           | 0.0002  | 0.0018 | fired    |

  Scenario: Any single trigger is sufficient
    Given an exposure whose quantitative trigger has not fired
      And whose obligor entered the watchlist this period
     When the SICR test runs
     Then the exposure moves to stage 2
      And the recorded trigger is the qualitative watchlist trigger

  Scenario: The 30-day backstop applies independently
    Given an exposure with 31 days past due
      And no quantitative or qualitative trigger
     When the SICR test runs
     Then the exposure moves to stage 2
      And the recorded trigger is the backstop
      And the exposure is included in the backstop-only population on RPT-005

  Scenario: Missing origination PD falls back and is disclosed
    Given an exposure with no retained lifetime PD at origination
     When the SICR test runs
     Then the quantitative test is not performed
      And the exposure is assessed on qualitative triggers and the backstop only
      And the exposure appears in the "missing origination PD" panel of RPT-005
      And the exposure is not silently assigned to stage 1

  Scenario: Low credit risk exemption is disallowed after any stage 2 history
    Given a corporate investment grade exposure currently rated investment grade
      And the exposure was in stage 2 in a prior period
     When the SICR test runs
     Then the low credit risk exemption is not applied

  Scenario: Backstop rebuttal is capped
    Given backstop rebuttals covering 6 percent of the stage 2 population by balance
     When the impairment run completes
     Then a blocking governance failure is raised
      And the run does not publish until the rebuttal population is within 5 percent
```

### AC-039 — ECL movement attribution

```gherkin
Feature: ECL movement attribution (BR-IMP-009)

  Scenario: The ten attribution causes sum exactly to the total movement
    Given a closing ECL balance at t0 and at t1
     When the movement attribution runs in the prescribed order
     Then the sum of new origination, derecognition, write-off, stage transfer,
          risk parameter change, scenario and weight change, overlay change,
          model change and foreign exchange equals the total movement
      And the residual line equals zero to the cent

  Scenario: A non-zero residual blocks publication
    Given the residual line is 1 cent
     When RPT-004 attempts to publish
     Then publication is blocked
      And the blocking reason names BR-IMP-009

  Scenario: Attribution order is not commutative and is fixed
    Given an exposure that both migrated stage and had its PD recalibrated
     When the attribution runs
     Then the stage transfer effect is measured holding risk parameters at t0
      And the risk parameter effect is measured holding stage at t1
      And reversing the order produces a different split, which is not permitted
```

### AC-088 — SAR confidentiality

```gherkin
Feature: SAR confidentiality across every access path (BR-AML-008, CTL-011)

  Scenario Outline: Direct column access
    Given a user in entitlement class "<class>"
     When they query compliance.aml_alert
     Then the columns sar_filed_flag and sar_filing_date are "<visibility>"

    Examples:
      | class | visibility |
      | ENT-1 | absent     |
      | ENT-2 | absent     |
      | ENT-3 | present    |
      | ENT-4 | absent     |
      | ENT-5 | absent     |
      | ENT-6 | present    |
      | ENT-7 | absent     |

  Scenario: Row exclusion rather than null return
    Given a user in entitlement class ENT-4
     When they query fraud.sar_filing
     Then zero rows are returned
      And no row is returned with nulled columns

  Scenario: The relationship manager view omits rather than masks
    Given a relationship manager in ENT-4 opens RPT-031 for an assigned client
      And that client is the subject of an open AML case
     When the report renders
     Then no AML field appears, masked or otherwise
      And no field appears whose only possible explanation is an AML case

  Scenario: Inference through a derived field is prevented
    Given an account restriction whose only cause in the data is a SAR
     When an ENT-4 user views that account
     Then the restriction is not displayed
      And no restriction reason code is displayed that maps uniquely to a SAR cause

  Scenario: Small-cell aggregate suppression
    Given an aggregate cell containing SAR-derived counts for 12 subjects
     When an ENT-2 user requests the aggregate
     Then the cell is suppressed
      And suppression applies below a threshold of 20 subjects

  Scenario: Export carries the restriction
    Given an ENT-4 user exports RPT-031 to a file
     When the export is inspected
     Then it contains no SAR-derived field

  Scenario: The denial message reveals nothing
    Given an ENT-4 user attempts to query fraud.sar_filing directly
     When access is denied
     Then the message states that the object is not available to their entitlement
      And does not state or imply that the object relates to suspicious activity reporting

  Scenario: Break-glass is approved, time-boxed and logged
    Given a platform engineer requires access to AML data for an incident
     When break-glass access is granted
     Then it is approved by P-07
      And it expires automatically
      And every object accessed is logged and reviewed
```

### AC-221 — Daily liquidity delivery

```gherkin
Feature: RPT-012 delivery by 09:00 (BR-LIQ-001, BR-DQ-012)

  Scenario: Complete data delivers a clean report
    Given contract DC-012 delivered MET at 04:30 local
      And every consumed dataset has a data quality score above threshold
     When RPT-012 runs
     Then it is available before 09:00 local
      And the LCR is published without qualification
      And the binding constraint entity, currency and consolidation level are stated

  Scenario: A missing feed does not delay publication
    Given contract DC-012 is MISSING at 08:00 local
     When RPT-012 runs
     Then it is still available before 09:00 local
      And the report carries a qualification banner
      And the banner names the missing feed and quantifies the population it would have contributed
      And the LCR figure is marked as qualified rather than suppressed

  Scenario: Late arrival triggers recomputation and reissue
    Given RPT-012 published qualified at 09:00
      And contract DC-012 delivers at 11:20
     When late arrival handling runs
     Then RPT-012 is recomputed and reissued
      And a restatement assessment is raised under BR-DQ-009
      And both the 09:00 version and the reissued version remain retrievable

  Scenario: Group surplus never masks a trapped-entity breach
    Given the group LCR is 142 percent
      And entity OA-BEU has an LCR of 96 percent
      And OA-BEU is subject to a liquidity transfer restriction
     When RPT-012 renders
     Then the binding constraint is identified as OA-BEU
      And the group figure is not presented as evidence of compliance for OA-BEU

  Scenario: Intraday peak is a maximum, not a snapshot
    Given intraday usage reached 96 percent of available liquidity at 14:20
      And end-of-day usage was 41 percent
     When RPT-012 renders the intraday section
     Then the peak of 96 percent and its time are displayed
      And the end-of-day figure is not presented as the intraday position
```

### AC-174 — Submission snapshot reproducibility

```gherkin
Feature: Frozen submission snapshots (BR-REG-004, ARCH-05)

  Scenario: A prior submission reproduces exactly
    Given a submission frozen with reference "COREP-2026Q1-OABEU-001"
     When the snapshot is reproduced from its retained inputs, parameters,
          model versions, FX rates and code version
     Then every output value matches the filed value exactly
      And any difference is a severity-1 defect

  Scenario: A restatement creates a new snapshot rather than editing one
    Given an error is found in a filed submission
     When the correction is made
     Then a new snapshot with a new version is created
      And the original snapshot remains retrievable and unchanged
      And the restatement is classified under BR-DQ-009

  Scenario: No privileged edit path exists
    Given a platform administrator with the highest available privilege
     When they attempt to modify a frozen snapshot
     Then the operation fails
      And the attempt is logged and reported to P-12 and P-14

  Scenario: As-reported and current views differ and both are available
    Given submission reference "FRY9C-2026Q1-001"
     When the same query is run in current mode and in as-reported mode
     Then both return results
      And the difference is attributable by BR-DQ-009 class
      And RPT-009 section 6 displays that attribution
```

### AC-254 — AML subject context performance and completeness

```gherkin
Feature: RPT-020 subject context panel

  Scenario: Context assembles from every relevant domain
    Given an investigator in ENT-3 selects a subject
     When the context panel loads
     Then it shows every account from the account domain
      And every related party from the BR-CRR-003 hierarchy traversal
      And every payment counterparty from the payment domain
      And every prior AML alert and case
      And every fraud alert on the same subject
      And KYC status, risk rating and the drivers of that rating

  Scenario: Context loads within the latency budget
    Given the production volumetrics of document 00 section 1.3
     When the context panel loads for a subject with 40 related parties
          and 200,000 transactions
     Then the panel renders within 5 seconds at the 95th percentile

  Scenario: Queue scoping restricts investigators to their assignments
    Given an investigator assigned to queue "EMEA-HIGH"
     When they open the alert queue
     Then only alerts assigned to that queue are returned
      And the team lead sees every queue
```

### AC-261 — Relationship manager scoping and prohibition

```gherkin
Feature: RPT-031 entitlement (BR-CUS-002, BR-AML-008)

  Scenario: Portfolio scoping is enforced at the catalog layer
    Given a relationship manager assigned to 42 client groups
     When they open RPT-031 without any filter
     Then only those 42 client groups are returned
      And the restriction is enforced by Unity Catalog, not by the report tool

  Scenario: A reassignment propagates within the refresh window
    Given a client group is reassigned to a different relationship manager
     When 15 minutes have elapsed
     Then the previous manager can no longer retrieve that group
      And the new manager can

  Scenario: Termination revokes immediately
    Given an employee termination event arrives from DC-025
     When the event is processed
     Then all access is revoked within 15 minutes
      And revocation does not wait for the next scheduled entitlement refresh

  Scenario: Same-day risk changes are visible
    Given a counterparty in the manager's portfolio is downgraded at 11:00
     When the manager opens RPT-031 at 11:30
     Then the downgrade appears in the recent changes panel

  Scenario: KYC status is visible only as an operational blocker
    Given an assigned client has an overdue high-risk KYC review
     When the manager opens RPT-031
     Then they see that a review is overdue and that it may block drawdown
      And they do not see the risk rating
      And they do not see the drivers of the risk rating
```

### AC-152 — Referential integrity at scale

```gherkin
Feature: Referential integrity (BR-DQ-002)

  Scenario: All declared foreign keys are validated each cycle
    Given the banking_ecm model declares 3,301 foreign keys
     When the integrity check runs
     Then every declared relationship is evaluated
      And the count of evaluated relationships is reported on RPT-038

  Scenario: An orphan on a CDE relationship blocks
    Given risk.credit_exposure contains a party_id with no matching customer.party row
     When the check runs
     Then a blocking failure is raised
      And promotion to Gold does not proceed

  Scenario: A placeholder parent is never created
    Given an orphan is detected
     When remediation runs
     Then no placeholder parent row is created
      And the orphan remains visible until the source system corrects it

  Scenario: A declared-nullable key with a null is not an orphan
    Given a nullable foreign key column contains null
     When the check runs
     Then no failure is raised
```

### AC-157 — Single metric definition

```gherkin
Feature: One implementation per certified metric (BR-DQ-007)

  Scenario: A duplicate implementation is detected
    Given a certified metric MET-005 exists in the Gold layer
      And a dashboard defines its own liquidity coverage ratio calculation
     When the weekly duplicate scan runs
     Then the duplicate is reported to P-12
      And it is reported even though it produces the same value

  Scenario: A report referencing the certified metric passes
    Given RPT-012 references MET-005 by identifier
     When the scan runs
     Then no duplicate is reported
```

---

## 4. Criteria index

Every criterion referenced in [02](./02-business-specifications.md) and [03](./03-reporting-requirements.md), with its level and its gate.

### 4.1 Business rule criteria

| AC | Proves | Level | Gate |
|---|---|---|---|
| AC-011 | `BR-CRR-001` population definition, including prospect and orphan handling | L2 | Gold promotion |
| AC-012 | `BR-CRR-002` measure hierarchy, netting-set scoping, over-collateralisation | L2 | Gold promotion |
| AC-013 | `BR-CRR-003` group traversal, detailed in section 3 | L2 | Gold promotion |
| AC-014 | `BR-CRR-004` large exposure, including missing capital base blocking | L3 | Certification |
| AC-015 | `BR-CRR-005` five dimensions, six pairs, HHI bands, `UNCLASSIFIED` in denominator | L3 | Certification |
| AC-016 | `BR-CRR-006` CCF application and unapproved-model fallback | L2 | Gold promotion |
| AC-017 | `BR-CRR-007` rating currency, staleness, 18-month standardised forcing | L2 | Gold promotion |
| AC-018 | `BR-CRR-008` override validity, four conditions, two-notch escalation | L2 | Gold promotion |
| AC-019 | `BR-CRR-009` all eight triggers, no suppression, re-entry on persisting condition | L2 | Gold promotion |
| AC-020 | `BR-CRR-010` NPL, contagion at 20 percent, 12-month cure probation | L2 | Gold promotion |
| AC-021 | `BR-CRR-011` utilisation on the limit's own basis and currency, FX split | L3 | Certification |
| AC-022 | `BR-CRR-012` appetite status by direction, null threshold as governance exception | L3 | Certification |
| AC-023 | `BR-CRR-013` financial and reporting breach distinction, cross-default, waiver expiry | L2 | Gold promotion |
| AC-024 | `BR-CRR-014` vintage immutability, exception isolation, uncleared application blocking | L2 | Gold promotion |
| AC-031 | `BR-IMP-001` dual basis, IFRS 9 to CECL bridge reconciles exactly | L3 | Certification |
| AC-032 | `BR-IMP-002` SICR, detailed in section 3 | L2 | Gold promotion |
| AC-033 | `BR-IMP-003` stage 3 equals NPL population | L5 | Sign-off |
| AC-034 | `BR-IMP-004` POCI never numeric-staged, never cures to stage 1 | L2 | Gold promotion |
| AC-035 | `BR-IMP-005` ECL formula, weights sum to one, original effective interest rate | L3 | Certification |
| AC-036 | `BR-IMP-006` identical scenario weights across portfolios | L2 | Gold promotion |
| AC-037 | `BR-IMP-007` valuation age by asset class, allocation without double count, lapsed liens | L2 | Gold promotion |
| AC-038 | `BR-IMP-008` overlay governance, four-quarter escalation, separate disclosure | L4 | Publication |
| AC-039 | `BR-IMP-009` attribution, detailed in section 3 | L3 | Certification |
| AC-040 | `BR-IMP-010` risk to finance at three grains | L5 | Sign-off |
| AC-041 | `BR-IMP-011` stage override governance and 3 percent cap | L2 | Gold promotion |
| AC-042 | `BR-IMP-012` write-off with matched provision release, recoveries not netted | L5 | Sign-off |
| AC-051 | `BR-CAP-001` recomputation within 1 basis point | L3 | Certification |
| AC-052 | `BR-CAP-002` combined buffer and distribution restriction | L3 | Certification |
| AC-053 | `BR-CAP-003` approach-specific RWA, floors applied before the formula | L3 | Certification |
| AC-054 | `BR-CAP-004` standardised parallel run present every period | L3 | Certification |
| AC-055 | `BR-CAP-005` leverage-specific CCFs distinct from credit CCFs | L3 | Certification |
| AC-056 | `BR-CAP-006` run immutability, no partial results, three scenarios minimum | L2 | Gold promotion |
| AC-057 | `BR-CAP-007` five-condition eligibility and quantified fallback | L2 | Gold promotion |
| AC-058 | `BR-CAP-008` allocation reconciles to 100 percent | L3 | Certification |
| AC-061 | `BR-LIQ-001` cap order 2B then 2A, inflow cap at reporting level, encumbrance at close | L3 | Certification |
| AC-062 | `BR-LIQ-002` NSFR with bucket roll-down identified | L3 | Certification |
| AC-063 | `BR-LIQ-003` binding constraint with transfer restriction respected | L4 | Publication |
| AC-064 | `BR-LIQ-004` intraday peak as maximum, throughput profile | L4 | Publication |
| AC-065 | `BR-LIQ-005` survival horizon with traceable behavioural assumptions | L3 | Certification |
| AC-066 | `BR-LIQ-006` component sum, zero-sum allocation, date-window enforcement | L3 | Certification |
| AC-067 | `BR-LIQ-007` ageing from value date, over-30-day escalation | L2 | Gold promotion |
| AC-071 | `BR-MKT-001` VaR compared on the limit's own basis, conversions shown | L3 | Certification |
| AC-072 | `BR-MKT-002` clean P&L basis, zone determination | L3 | Certification |
| AC-073 | `BR-MKT-003` netting evidence required, CVA reported gross, wrong-way identified | L2 | Gold promotion |
| AC-074 | `BR-MKT-004` partial settlement as fail, cause attribution | L2 | Gold promotion |
| AC-075 | `BR-COL-001` staleness applied in every context, not only impairment | L2 | Gold promotion |
| AC-076 | `BR-COL-002` dispute distinct from unmet, cure-period escalation | L2 | Gold promotion |
| AC-077 | `BR-COL-003` wrong-way collateral ineligible, three concurrent concentration limits | L2 | Gold promotion |
| AC-081 | `BR-AML-001` PEP never below high, sanctioned forces prohibited | L2 | Gold promotion |
| AC-082 | `BR-AML-002` complete requires approved, transacting versus dormant split | L2 | Gold promotion |
| AC-083 | `BR-AML-003` chains resolve to natural persons, senior officials fallback | L2 | Gold promotion |
| AC-084 | `BR-AML-004` list version recorded, false positive rate by list and algorithm | L2 | Gold promotion |
| AC-085 | `BR-AML-005` SLA matrix, reassignment does not reset, closure reason required | L2 | Gold promotion |
| AC-086 | `BR-AML-006` alert merge on same subject, no-action recorded as a decision | L2 | Gold promotion |
| AC-087 | `BR-AML-007` clock from detection date, non-business days do not extend | L2 | Gold promotion |
| AC-088 | `BR-AML-008` confidentiality, detailed in section 3 | L5 | Release, quarterly re-test |
| AC-089 | `BR-AML-009` typology coverage completeness, rare-typology distinction | L4 | Publication |
| AC-090 | `BR-AML-010` lookback alerts carry original transaction dates and current detection date | L2 | Gold promotion |
| AC-091 | `BR-FRD-001` gross, recovery and net distinct; recognition periods differ | L3 | Certification |
| AC-092 | `BR-FRD-002` version change marked on every trend | L4 | Publication |
| AC-093 | `BR-FRD-003` linkage strength scoring, single-attribute links below threshold excluded | L2 | Gold promotion |
| AC-094 | `BR-FRD-004` stage deadlines, missed representment as operational loss | L2 | Gold promotion |
| AC-101 | `BR-PAY-001` automated repair disqualifies, four-way dimensional split | L3 | Certification |
| AC-102 | `BR-PAY-002` cut-off priority over age, static-data routing | L4 | Publication |
| AC-103 | `BR-PAY-003` no settled row without completed screening | L1 | Silver promotion |
| AC-104 | `BR-CHN-001` partial degradation counts, customer-impacting minutes weighting | L3 | Certification |
| AC-105 | `BR-CHN-002` cross-channel stitching, customer wait excluded and visible | L3 | Certification |
| AC-106 | `BR-CHN-003` normalised volume, 50 percent theme growth escalation | L3 | Certification |
| AC-111 | `BR-FIN-001` balance in both currencies, preparer differs from approver | L1 | Silver promotion |
| AC-112 | `BR-FIN-002` late-period high-value journals listed individually | L4 | Publication |
| AC-113 | `BR-FIN-003` control-account grain, no cross-account netting | L5 | Sign-off |
| AC-114 | `BR-FIN-004` predecessor enforcement, critical path recomputed on change | L4 | Publication |
| AC-115 | `BR-FIN-005` residual investigated, only translation permitted non-zero | L5 | Sign-off |
| AC-116 | `BR-FIN-006` segments plus unallocated equals group exactly | L5 | Sign-off |
| AC-121 | `BR-CUS-001` merge is not delete, pre-merge history reproducible, no auto-merge | L2 | Gold promotion |
| AC-122 | `BR-CUS-002` assignment-derived access, immediate revocation on termination | L5 | Release |
| AC-123 | `BR-CUS-003` immediate consent withdrawal propagation, retention conflict recorded | L2 | Gold promotion |
| AC-131 | `BR-MDL-001` rules and scorecards in inventory, no model computed in a report | L4 | Publication |
| AC-132 | `BR-MDL-002` frequency by risk rating, escalation lead times | L4 | Publication |
| AC-133 | `BR-MDL-003` degradation against baseline not prior period, population stability | L3 | Certification |
| AC-134 | `BR-MDL-004` unapproved use blocks | L2 | Gold promotion |
| AC-135 | `BR-MDL-005` bidirectional, transitive model-to-metric dependency | L3 | Certification |
| AC-136 | `BR-ORX-001` three dates required, boundary events flagged once | L2 | Gold promotion |
| AC-137 | `BR-ORX-002` six required KRI attributes, data quality flag visible | L2 | Gold promotion |
| AC-141 | `BR-AUD-001` audit validation required for closure, extensions counted, repeats upgraded | L2 | Gold promotion |
| AC-142 | `BR-AUD-002` segregation gap detection | L4 | Publication |
| AC-151 | `BR-DQ-001` CDE derived from lineage, no unowned CDE | L4 | Publication |
| AC-152 | `BR-DQ-002` integrity, detailed in section 3 | L1 | Silver promotion |
| AC-153 | `BR-DQ-003` acyclic, rooted, within depth | L1 | Silver promotion |
| AC-154 | `BR-DQ-004` all ten reconciliations within tolerance | L5 | Sign-off |
| AC-155 | `BR-DQ-005` domain and pattern conformance, defensive casts on `STRING` numerics | L1 | Silver promotion |
| AC-156 | `BR-DQ-006` thresholds by criticality | L1 | Silver promotion |
| AC-157 | `BR-DQ-007` duplicate detection, detailed in section 3 | L3 | Certification |
| AC-158 | `BR-DQ-008` freshness against contract, staleness displayed | L4 | Publication |
| AC-159 | `BR-DQ-009` classification, quantification, approval, disclosure | L5 | Sign-off |
| AC-160 | `BR-DQ-010` no publication before reconciliation passes or is qualified | L4 | Publication |
| AC-161 | `BR-DQ-011` FX recomputation within 1 basis point | L2 | Gold promotion |
| AC-162 | `BR-DQ-012` late arrival by report class, gap named and quantified | L4 | Publication |
| AC-163 | `BR-DQ-013` weighted score, 0.80 cap while blocking rules fail | L3 | Certification |
| AC-171 | `BR-REG-001` population lock and prior-period arrival identification | L5 | Submission |
| AC-172 | `BR-REG-002` every validation rule executed, failures corrected or explained | L5 | Submission |
| AC-173 | `BR-REG-003` return to ledger bridge produced and retained | L5 | Submission |
| AC-174 | `BR-REG-004` snapshot reproducibility, detailed in section 3 | L5 | Submission |
| AC-175 | `BR-REG-005` counterparty reference completeness including protection providers | L5 | Submission |
| AC-176 | `BR-REG-006` no report-level derivation of missing attributes | L5 | Submission |
| AC-177 | `BR-REG-007` disclosure equals submission, reconciling items explicit | L5 | Submission |
| AC-178 | `BR-REG-008` four-hour ad-hoc service level met at production scale | L6 | Release |

### 4.2 Report criteria

| AC | Report | Additionally proves |
|---|---|---|
| AC-201 | RPT-001 | Escalation displayed with every red status; blocking-rule suppression visible |
| AC-202 | RPT-002 | Governance exception panel; near-amber deterioration highlighted |
| AC-203 | RPT-016 | Incomplete runs listed with results suppressed, visibly |
| AC-204 | RPT-003 | Every exposure figure labelled with its measure; four-hour ad-hoc reproduction |
| AC-205 | RPT-004 | Zero residual; model, overlay and final shown separately; drill respects entitlement |
| AC-206 | RPT-005 | Backstop-only proportion present without reconfiguration |
| AC-207 | RPT-006 | All triggers on one row; AML data absent for P-11 |
| AC-208 | RPT-007 | Near-breach panel; reporting breaches distinct from financial |
| AC-209 | RPT-008 | Exception lending isolated in every vintage cut |
| AC-210 | RPT-018 | Netting benefit shown with supporting agreement; CVA gross |
| AC-211 | RPT-019 | Disputes distinct from unmet; wrong-way collateral identified |
| AC-212 | RPT-017 | Conversion method displayed; book hierarchy matches limit scope |
| AC-221 | RPT-012 | Detailed in section 3 |
| AC-222 | RPT-013 | Roll-down attribution line present |
| AC-223 | RPT-014 | Outstanding ALCO resolutions carried with owner and due date |
| AC-224 | RPT-015 | Five FTP components shown; zero-sum check displayed |
| AC-231 | RPT-009 | As-reported comparison section; validation failures with approver |
| AC-232 | RPT-010 | Y-9C reconciliation; population movement explained |
| AC-233 | RPT-011 | No submission with incomplete counterparty reference data |
| AC-241 | RPT-028 | Critical path recomputed on status change within 15 minutes |
| AC-242 | RPT-029 | Sub-materiality differences carry owner and age |
| AC-243 | RPT-030 | Segments plus unallocated equals group; check displayed |
| AC-244 | RPT-026 | Four-way STP split; cut-off ordering |
| AC-245 | RPT-027 | Over-30-day items raised as operational loss events |
| AC-251 | RPT-021 | Ordered by time remaining; runs on non-business days; ENT-3 only |
| AC-252 | RPT-022 | P-11 sees due status only, never rating or drivers |
| AC-253 | RPT-023 | 98 percent false positive flag; released-on-pending at the top |
| AC-254 | RPT-020 | Detailed in section 3 |
| AC-255 | RPT-024 | Loss and recovery recognised in their own periods; customer friction shown |
| AC-256 | RPT-025 | Version change marked; rare-typology rules distinguished from noisy ones |
| AC-261 | RPT-031 | Detailed in section 3 |
| AC-262 | RPT-032 | Partial degradation counted; customer-impacting minutes weighted |
| AC-263 | RPT-033 | Normalised volume; 50 percent theme growth escalation |
| AC-271 | RPT-038 | Blocking failures first; CDE ownership gaps present |
| AC-272 | RPT-039 | Lineage generated from deployed code; impact analysis returns in seconds |
| AC-273 | RPT-034 | Regulatory-impact section answers the model dependency question as a query |
| AC-274 | RPT-035 | High override rate framed as a model signal |
| AC-275 | RPT-036 | Management assertion is not closure; triple extensions escalate |
| AC-276 | RPT-037 | Three dates shown; flagged-data KRIs visually distinct |
| AC-277 | RPT-040 | Restriction breach and allocation drift not merged |

---

## 5. Test data strategy

| Requirement | Approach |
|---|---|
| Volume | Synthetic data generated at the [00, section 1.3](./00-programme-charter-and-scope.md#13-scale-assumptions) volumetrics, with referential integrity guaranteed |
| Edge coverage | Every named edge case in [02](./02-business-specifications.md) has a seeded fixture. An edge case with no fixture is untested and the rule is not accepted |
| Production data | Never used in a non-production environment unmasked. Masked extracts follow the [06, section 1.3](./06-governance-security-and-controls.md#13-column-masking) policy, and SAR-related data is never extracted at all |
| Time travel | Historical fixtures spanning at least eight quarter ends, so that bitemporal and vintage criteria are testable |
| Regulatory fixtures | Known-answer fixtures derived from published supervisory worked examples, so that `TP-04` independence holds |

## 6. Test environments

| Environment | Data | Used for |
|---|---|---|
| Development | Small synthetic | L1, L2 |
| Integration | Full synthetic at volume | L1 to L4, L6 |
| Pre-production | Masked production extract, no SAR data | L4, L5, L7 |
| Production | Live | L5 continuous reconciliation, L6 monitoring |

## 7. Release gates

A release proceeds only when all of the following hold. There is no partial gate.

1. Every L1 and L2 criterion passes
2. Every L3 criterion passes for metrics affected by the change
3. Every L4 criterion passes for reports affected by the change
4. Every L5 reconciliation is within tolerance or is explicitly qualified by a named approver
5. L6 criteria pass at production volumetrics, including `AC-178` and the `RPT-020` context latency in `AC-254`
6. `AC-088` passes in full, tested from every entitlement class, with no exception
7. The owning persona has signed L7 acceptance for every changed report
8. Lineage regenerates and `RPT-039` reflects the change

## 8. Regulatory traceability matrix

| Driver | Business rules | Reports | Criteria |
|---|---|---|---|
| FFIEC 031 Call Report | `BR-CRR-001`, `BR-CRR-010`, `BR-IMP-001`, `BR-FIN-003` | RPT-009, RPT-029 | AC-011, AC-020, AC-031, AC-113 |
| FR Y-9C | `BR-CAP-001` to `BR-CAP-005`, `BR-REG-003` | RPT-009, RPT-010 | AC-051 to AC-055, AC-173 |
| FR Y-14A/Q/M | `BR-CRR-001`, `BR-CRR-014`, `BR-CAP-006`, `BR-REG-006` | RPT-010, RPT-016 | AC-011, AC-024, AC-056, AC-176 |
| FR 2052a | `BR-LIQ-001`, `BR-LIQ-004`, `BR-DQ-012` | RPT-012 | AC-061, AC-064, AC-162, AC-221 |
| CCAR / DFAST | `BR-CAP-006`, `BR-IMP-006`, `BR-MDL-004` | RPT-016 | AC-056, AC-036, AC-134 |
| BSA SAR and CTR | `BR-AML-005` to `BR-AML-007` | RPT-020, RPT-021 | AC-085 to AC-087, AC-251 |
| 31 CFR 1020.320(e) | `BR-AML-008` | every report | AC-088 |
| OFAC sanctions | `BR-AML-004`, `BR-PAY-003` | RPT-023, RPT-026 | AC-084, AC-103, AC-253 |
| CRR / CRD COREP | `BR-CAP-001` to `BR-CAP-004`, `BR-CRR-004` | RPT-009 | AC-051 to AC-054, AC-014 |
| FINREP | `BR-IMP-001`, `BR-CRR-010`, `BR-FIN-003` | RPT-004, RPT-029 | AC-031, AC-020, AC-113 |
| AnaCredit | `BR-REG-005`, `BR-CRR-001`, `BR-DQ-006` | RPT-011 | AC-175, AC-011, AC-156 |
| LCR / NSFR ITS | `BR-LIQ-001` to `BR-LIQ-003` | RPT-012, RPT-013 | AC-061 to AC-063 |
| PRA110 | `BR-LIQ-005` | RPT-013, RPT-014 | AC-065 |
| EMIR / MiFIR | `BR-MKT-003`, `BR-MKT-004` | RPT-018 | AC-073, AC-074 |
| IFRS 9 | `BR-IMP-001` to `BR-IMP-012` | RPT-004, RPT-005 | AC-031 to AC-042 |
| ASC 326 CECL | `BR-IMP-001`, `BR-IMP-005` | RPT-004 | AC-031, AC-035 |
| Basel III finalisation | `BR-CAP-003`, `BR-CAP-004`, `BR-CRR-006` | RPT-009, RPT-016 | AC-053, AC-054, AC-016 |
| BCBS 239 | the whole of [06](./06-governance-security-and-controls.md) | RPT-038, RPT-039 | AC-271, AC-272 |
| SOX 404 | `BR-FIN-001` to `BR-FIN-005`, `BR-AUD-002` | RPT-028, RPT-029 | AC-111 to AC-115, AC-142 |
| Pillar 3 | `BR-REG-007` | RPT-009 | AC-177 |
| GDPR / CCPA | `BR-CUS-003` | RPT-038 | AC-123 |
| 6AMLD | `BR-AML-001` to `BR-AML-003` | RPT-022 | AC-081 to AC-083 |
