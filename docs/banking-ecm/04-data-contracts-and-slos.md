# 04 — Data Contracts and Freshness Service Level Objectives

**Document ID:** OAFG-BSR-2026-04 · **Version:** 1.0 · **Owner:** Chief Data Officer (P-12) · **Approvers:** each source system owner

---

## 1. What a data contract is here

A data contract is a binding, testable agreement between a source system owner and the platform. It states what arrives, when, at what quality, and what happens when it does not. It is not a schema document, and it is not a description of current behaviour. It is a commitment.

A contract has five parts and is incomplete without all five.

| Part | Content |
|---|---|
| **Payload** | The `banking_ecm` tables populated, the grain, and the change-capture mode |
| **Schedule** | Delivery window, expressed against a named clock and time zone |
| **Quality** | The rules from [02, Part K](./02-business-specifications.md#part-k--data-quality) that must pass at ingestion |
| **Change** | How schema and semantic changes are notified, and the minimum notice |
| **Breach** | The defined consequence when the contract is not met |

## 2. Contract states

| State | Meaning | Consequence |
|---|---|---|
| `MET` | Delivered on time, quality passed | Normal processing |
| `LATE` | Delivered after the window, quality passed | `BR-DQ-012` late-arrival handling. Counted against the breach tolerance |
| `PARTIAL` | Delivered on time, incomplete population | Processed with the gap quantified. Downstream reports qualified |
| `FAILED` | Quality rules failed at blocking severity | Not promoted to Silver. Prior period's data remains current. Incident raised |
| `MISSING` | Not delivered within the window plus the grace period | Downstream reports publish qualified or do not publish, per their own quality gate |

**Breach tolerance.** Three `LATE`, `PARTIAL`, `FAILED` or `MISSING` occurrences in a rolling quarter constitutes a contract breach, escalated to the source system owner and to P-12, and reported on `RPT-038`. There is no tolerance at all for `FAILED` on a contract feeding a daily regulatory report.

## 3. Clocks

All windows are expressed against one of three clocks. Mixing them is the most common cause of a contract that looks met and is not.

| Clock | Definition |
|---|---|
| `BD` | OAFG group business day, New York calendar, close at 18:00 America/New_York |
| `LOCAL` | The delivering entity's local business day and calendar |
| `UTC` | Wall-clock UTC, used only for continuous feeds with no business-day concept |

---

## 4. Contract register

### 4.1 Core banking and customer

#### DC-001 — Party and customer master
| | |
|---|---|
| Source | Temenos T24, FIS Profile (customer master) |
| Owner | Head of Core Banking Platforms |
| Populates | `customer.party`, `customer.individual_profile`, `customer.corporate_profile`, `customer.party_address`, `customer.party_contact`, `customer.party_identifier`, `customer.party_lifecycle_event` |
| Grain | One row per party per change |
| Mode | Change data capture, SCD type 2 on `customer.party` |
| Window | Continuous, with a completeness checkpoint at 22:00 `BD` |
| Quality | `BR-DQ-002` on all party foreign keys, `BR-DQ-005` on `kyc_status`, `risk_rating`, `lifecycle_status`, `customer_segment`, `citizenship_country_code`, `residency_status`; `BR-DQ-006` at regulatory-CDE threshold on `legal_name`, `tax_identification_number`, `country_id` |
| Change notice | 20 business days for schema change, 40 for semantic change |
| Consumers | Every report. This is the highest-fan-out contract in the platform |
| Breach consequence | `FAILED` blocks all downstream promotion. No exception path |

#### DC-002 — Deposit accounts and balances
| | |
|---|---|
| Source | Temenos T24, FIS Profile |
| Owner | Head of Core Banking Platforms |
| Populates | `account.deposit_account`, `account.balance`, `account.holder`, `account.status_history`, `account.account_limit`, `account.hold` |
| Grain | One row per account per balance date |
| Mode | Full daily snapshot of balances, CDC on account master |
| Window | 02:00 `BD` for the prior business day |
| Quality | `BR-DQ-004` reconciliation 5 against the ledger control account, tolerance USD 1 per account |
| Consumers | RPT-012, RPT-013, RPT-029, RPT-030, RPT-031 |

#### DC-003 — Account transactions
| | |
|---|---|
| Source | Temenos T24 |
| Owner | Head of Core Banking Platforms |
| Populates | `account.account_transaction`, `account.interest_accrual`, `account.account_fee` |
| Grain | One row per posting |
| Mode | Append only, immutable |
| Window | Micro-batch every 15 minutes, day complete by 01:00 `BD` |
| Quality | No late-arriving postings beyond T+2. A posting arriving beyond T+2 is a `PARTIAL` on the original day and triggers restatement assessment under `BR-DQ-009` |
| Consumers | RPT-020 subject context, RPT-024, RPT-026, RPT-029 |

### 4.2 Lending and credit

#### DC-004 — Loan accounts and facilities
| | |
|---|---|
| Source | nCino, Loan IQ, T24 lending module |
| Owner | Head of Lending Technology |
| Populates | `loan.loan_account`, `loan.facility`, `loan.drawdown`, `loan.repayment`, `loan.amortization_schedule`, `loan.modification`, `loan.write_off`, `loan.disbursement` |
| Grain | One row per loan account, one row per facility |
| Mode | Full daily snapshot plus CDC on status changes |
| Window | 03:00 `BD` |
| Quality | `BR-DQ-005` cast validation on `days_past_due` (blocking, it is a CDE); `BR-DQ-004` reconciliations 1 and 3; `BR-DQ-006` at regulatory threshold on `outstanding_principal_balance`, `origination_date`, `maturity_date`, `npl_classification` |
| Consumers | RPT-003 to RPT-008, RPT-010, RPT-011, RPT-031 |
| Breach consequence | `FAILED` blocks RPT-004, RPT-005, RPT-010, RPT-011 |

#### DC-005 — Credit applications
| | |
|---|---|
| Source | nCino |
| Owner | Head of Lending Technology |
| Populates | `loan.credit_application`, `loan.credit_review`, `loan.pricing` |
| Window | 04:00 `BD` |
| Quality | Decision-time attributes must be immutable after decision. A changed `credit_score` or `dscr` on a decided application is a blocking failure, because it destroys vintage analysis under `BR-CRR-014` |
| Consumers | RPT-008 |

#### DC-006 — Covenants
| | |
|---|---|
| Source | Loan IQ, covenant tracking system |
| Owner | Head of Credit Administration |
| Populates | `loan.covenant`, `loan.covenant_package` |
| Window | 04:00 `BD`, and within 2 hours of any waiver or amendment |
| Quality | Every covenant must have `threshold_value`, `threshold_operator`, `measurement_frequency` and `facility_id`. Missing any is blocking |
| Consumers | RPT-006, RPT-007, RPT-031 |

### 4.3 Risk

#### DC-007 — Credit exposure and risk parameters
| | |
|---|---|
| Source | Risk engine (internal), Murex for derivative exposure |
| Owner | Head of Risk Technology |
| Populates | `risk.credit_exposure`, `risk.counterparty_rating`, `risk.concentration_risk`, `risk.risk_limit` |
| Grain | One row per exposure per `measurement_date` |
| Mode | Full snapshot per measurement date, immutable once complete |
| Window | 05:00 `BD` for daily exposure; 05:00 on `BD+2` for month-end |
| Quality | `BR-DQ-004` reconciliations 3, 4 and 10; `BR-DQ-011` FX verification; `BR-CRR-002` measure hierarchy validation; `BR-DQ-006` at regulatory threshold on `ead`, `pd`, `lgd`, `rwa_credit`, `exposure_class` |
| Consumers | RPT-001, RPT-003, RPT-004, RPT-009, RPT-016, RPT-018 |
| Breach consequence | `FAILED` blocks RPT-001, RPT-003, RPT-009 and every capital submission |

#### DC-008 — Impairment
| | |
|---|---|
| Source | ECL engine |
| Owner | Head of Risk Technology |
| Populates | `risk.risk_ecl_provision`, `loan.loan_ecl_provision` |
| Window | 06:00 on `BD+2` after month end |
| Quality | Scenario weights sum to 1.0000 (`BR-IMP-005`, blocking); stage 3 to NPL agreement (`BR-IMP-003`, blocking); POCI stage validity (`BR-IMP-004`, blocking); `BR-DQ-004` reconciliation 2 with zero tolerance |
| Consumers | RPT-001, RPT-004, RPT-005, RPT-009, RPT-010, RPT-011, RPT-028 |

#### DC-009 — Stress testing
| | |
|---|---|
| Source | Stress engine |
| Owner | Head of Stress Testing |
| Populates | `risk.stress_test_run`, `risk.stress_scenario`, `risk.scenario_result`, `risk.stress_test_factor_result`, `loan.stress_projection` |
| Window | Event-driven, on run completion |
| Quality | A run is delivered complete or not at all. Partial runs are rejected, per `BR-CAP-006` |
| Consumers | RPT-016, RPT-001 |

#### DC-010 — Operational risk and key risk indicators
| | |
|---|---|
| Source | Operational risk management system |
| Owner | Head of Operational Risk |
| Populates | `risk.operational_risk_event`, `risk.kri_measurement`, `risk.assessment` |
| Window | 08:00 `BD` |
| Quality | Event date, discovery date and accounting date all populated (`BR-ORX-001`, blocking); all six KRI attributes present (`BR-ORX-002`, blocking) |
| Consumers | RPT-001, RPT-037 |

#### DC-011 — Model metadata and performance
| | |
|---|---|
| Source | Model risk management system |
| Owner | P-13 |
| Populates | `risk.irb_model`, `risk.model_validation`, `risk.model_deployment`, `risk.valuation_model` |
| Window | Weekly, 08:00 Monday `BD`, and within 4 hours of any approval status change |
| Quality | Approval status, effective dates and validation dates all populated for any model in use. `BR-MDL-004` unapproved use detection runs at ingestion |
| Consumers | RPT-034, RPT-035, and the eligibility gate on RPT-009 |

### 4.4 Treasury and finance

#### DC-012 — Liquidity and capital
| | |
|---|---|
| Source | Treasury system, ALM engine |
| Owner | Head of Treasury Technology |
| Populates | `treasury.liquidity_ratio`, `treasury.hqla_inventory`, `treasury.capital_ratio`, `treasury.liquidity_position`, `treasury.cash_flow_forecast`, `risk.liquidity_metric` |
| Grain | One row per entity per currency per consolidation level per reporting date |
| Window | **04:30 `LOCAL` on T+1.** This window exists to make the 09:00 RPT-012 deadline achievable with a four-and-a-half-hour margin |
| Quality | `data_quality_score` populated on every row (blocking); HQLA level amounts sum to `total_hqla_amount`; `BR-CAP-001` ratio recomputation within 1 basis point |
| Consumers | RPT-001, RPT-009, RPT-012, RPT-013, RPT-014, RPT-016 |
| Breach consequence | A `MISSING` on this contract does not delay RPT-012. The report publishes at 09:00 qualified, per `BR-DQ-012`. The contract breach is escalated to the source owner the same morning |

#### DC-013 — Funds transfer pricing
| | |
|---|---|
| Source | ALM engine |
| Owner | Head of Treasury Technology |
| Populates | `treasury.ftp_rate`, `treasury.ftp_allocation`, `treasury.transfer_pricing_curve` |
| Window | 06:00 `BD+3` after month end |
| Quality | Component sum equals `composite_rate_bps` (blocking); allocation sums to zero across all lines of business plus treasury residual, tolerance USD 1,000 (blocking), per `BR-LIQ-006` |
| Consumers | RPT-014, RPT-015, RPT-030, RPT-031 |

#### DC-014 — General ledger
| | |
|---|---|
| Source | Oracle EBS, SAP |
| Owner | Group Financial Controller (P-06) |
| Populates | `ledger.journal_entry`, `ledger.journal_entry_line`, `ledger.gl_account`, `ledger.trial_balance`, `ledger.accounting_period`, `ledger.legal_entity`, `ledger.subledger_reconciliation`, `ledger.financial_close_task` |
| Window | Continuous during close, complete by 20:00 `BD` each close day |
| Quality | Every journal balances in both currencies (`BR-FIN-001`, blocking); `preparer_name <> approver_name` (blocking); `BR-DQ-004` reconciliations 1 and 5 |
| Consumers | RPT-004, RPT-009, RPT-028, RPT-029, RPT-030 |

#### DC-015 — Nostro statements
| | |
|---|---|
| Source | Correspondent bank statements via SWIFT MT940 and camt.053 |
| Owner | Head of Payment Operations |
| Populates | `treasury.nostro_account`, `treasury.nostro_reconciliation` |
| Window | 07:00 `LOCAL` on T+1 per correspondent |
| Quality | Statement closing balance must reconcile to the movement sum. A statement that does not internally reconcile is rejected, not loaded |
| Consumers | RPT-027, RPT-012 |
| Note | This contract is with an external party. Where a correspondent is persistently late, the remedy is commercial, not technical, and P-04 owns that conversation |

### 4.5 Payments and channels

#### DC-016 — Payment transactions
| | |
|---|---|
| Source | Payment hub, SWIFT gateway, card processor |
| Owner | Head of Payments Engineering |
| Populates | `payment.payment_transaction`, `payment.instruction`, `payment.status_event`, `payment.exception`, `payment.return`, `payment.swift_message`, `payment.card_transaction` |
| Grain | One row per payment per status event |
| Mode | Streaming, at-least-once with idempotent keys |
| Window | Continuous, maximum 5-minute lag `UTC` |
| Quality | `sanctions_screening_status` populated before any row with `settlement_status` of settled (`BR-PAY-003`, blocking); duplicate detection on reference number |
| Consumers | RPT-012, RPT-020, RPT-024, RPT-026, RPT-027 |

#### DC-017 — Channel sessions and interactions
| | |
|---|---|
| Source | Digital platform, contact centre, branch systems, ATM network |
| Owner | Head of Channel Engineering |
| Populates | `channel.session`, `channel.interaction`, `channel.journey_instance`, `channel.sla_breach`, `channel.channel_incident`, `channel.atm_transaction`, `channel.branch_teller_transaction` |
| Mode | Streaming |
| Window | Continuous, maximum 2-minute lag `UTC` |
| Quality | Session start and end timestamps consistent; `sla_target_response_time_ms` populated for every measured interaction |
| Consumers | RPT-024, RPT-026, RPT-032 |

### 4.6 Financial crime and fraud

#### DC-018 — AML alerts and cases
| | |
|---|---|
| Source | Actimize |
| Owner | Head of Financial Crime Technology |
| Populates | `compliance.aml_alert`, `compliance.aml_case`, `compliance.monitoring_rule`, `compliance.rule_validation`, `compliance.coverage` |
| Mode | Streaming for alerts, CDC for cases |
| Window | Continuous, maximum 10-minute lag `UTC` |
| Quality | `detection_date` and `detection_timestamp` populated on every alert (blocking, because the filing clock depends on them per `BR-AML-007`); `sla_deadline` derived and populated; every alert linked to a `monitoring_rule_id` |
| Consumers | RPT-020, RPT-021, RPT-023 |
| Access | Ingestion and storage subject to `BR-AML-008` from the moment of landing, including in Bronze |

#### DC-019 — KYC and sanctions screening
| | |
|---|---|
| Source | Onboarding platform, Fircosoft |
| Owner | Head of Financial Crime Technology |
| Populates | `compliance.kyc_review`, `compliance.sanctions_screening_event`, `compliance.sanctions_list_entry`, `customer.customer_beneficial_owner`, `customer.kyc_record` |
| Window | Continuous for screening; 06:00 `BD` for review status |
| Quality | Sanctions list version recorded on every screening event (blocking); `next_review_due_date` populated on every completed review |
| Consumers | RPT-022, RPT-023, RPT-008 |

#### DC-020 — Fraud alerts and losses
| | |
|---|---|
| Source | Falcon, Featurespace, internal case system |
| Owner | Head of Fraud Technology |
| Populates | `fraud.fraud_alert`, `fraud.case`, `fraud.loss`, `fraud.loss_recovery`, `fraud.chargeback`, `fraud.detection_rule`, `fraud.rule_performance`, `fraud.device_fingerprint`, `fraud.network_link` |
| Mode | Streaming |
| Window | Continuous, maximum 3-minute lag `UTC` |
| Quality | Card numbers truncated at source to last four digits; `loss_amount` and `recovery_amount` both non-negative with recovery never exceeding loss (`BR-FRD-001`, blocking) |
| Consumers | RPT-024, RPT-025, RPT-037, and the fraud panel of RPT-020 |

### 4.7 Reference, audit and corporate

#### DC-021 — Reference data
| | |
|---|---|
| Source | Bloomberg, Refinitiv, GLEIF, internal reference master |
| Owner | Head of Reference Data |
| Populates | the whole `reference` schema, plus `security.instrument`, `security.price`, `security.credit_rating`, `security.corporate_action` |
| Window | 01:00 `BD` for static reference; market data continuous |
| Quality | Every currency, country, instrument and industry code referenced by transactional data must exist (`ASM-06`, `BR-DQ-002`, blocking); exchange rates present for every currency pair used |
| Consumers | Every report |
| Note | This is the contract whose failure produces the largest number of apparently unrelated downstream failures. It is monitored first in every incident |

#### DC-022 — Collateral
| | |
|---|---|
| Source | Murex, Calypso, collateral management system |
| Owner | Head of Collateral Operations |
| Populates | the `collateral` schema |
| Window | 05:00 `BD`, and every 30 minutes during market hours for margin calls |
| Quality | Valuation date populated on every valuation; haircut schedule current; ISDA and CSA references resolvable for any claimed netting benefit (`BR-MKT-003`, blocking) |
| Consumers | RPT-018, RPT-019, RPT-004, RPT-011 |

#### DC-023 — Trading and positions
| | |
|---|---|
| Source | Murex, Calypso |
| Owner | Head of Markets Technology |
| Populates | the `trade` schema, `risk.market_risk_position` |
| Window | 04:00 `BD` |
| Quality | Trade to position reconciliation; settlement instruction present for every trade |
| Consumers | RPT-017, RPT-018 |

#### DC-024 — Audit and compliance findings
| | |
|---|---|
| Source | Internal audit management system, regulatory exam tracker |
| Owner | P-14 |
| Populates | the `audit` schema, `compliance.regulatory_exam`, `compliance.exam_finding`, `compliance.breach`, `compliance.obligation`, `compliance.consent_order` |
| Window | 06:00 `BD` |
| Quality | Every finding has a rating, owner, action and due date (`BR-AUD-001`, blocking) |
| Consumers | RPT-036, RPT-037 |

#### DC-025 — Human resources
| | |
|---|---|
| Source | Workday |
| Owner | Chief Human Resources Officer |
| Populates | `hr.employee`, `hr.hr_position`, `hr.org_unit`, `hr.license_certification`, `hr.regulatory_disclosure` |
| Window | Hourly for employment status, daily for the remainder |
| Quality | Termination events must propagate within 15 minutes for entitlement revocation, per `BR-CUS-002`. This is the only HR attribute with a sub-hourly requirement, and it is a security control |
| Consumers | Entitlement resolution for every report; RPT-035 analyst attribution |

#### DC-026 — Wealth and asset management
| | |
|---|---|
| Source | Portfolio management system, transfer agency |
| Owner | Head of Wealth Technology |
| Populates | the `wealth` and `asset` schemas |
| Window | 05:00 `BD` |
| Quality | NAV present for every valuation date; mandate and investment policy statement resolvable for every managed portfolio |
| Consumers | RPT-040, RPT-030, RPT-031 |

---

## 5. Freshness service level objectives

The SLO is the maximum age of data at the moment a report is served, measured from the data's `as_of_date` close.

| Dataset group | Contracts | Freshness SLO | Consuming latency class |
|---|---|---|---|
| Payments, channels, fraud, AML alerts | DC-016, DC-017, DC-018, DC-020 | 10 minutes | Near real time and sub-hourly |
| Collateral margin calls | DC-022 | 30 minutes | Intraday |
| Liquidity and capital | DC-012 | 4.5 hours from local close | RPT-012 at 09:00 |
| Credit exposure, loans, covenants | DC-004, DC-006, DC-007 | 8 hours | Next business day |
| Reference data | DC-021 | 8 hours | All |
| Ledger during close | DC-014 | 1 hour | Sub-hourly |
| Impairment | DC-008 | 2 business days from month end | Close cycle |
| Model metadata | DC-011 | 7 days, 4 hours on approval change | Close cycle |

**SLO breach handling.** A freshness SLO breach is reported on `RPT-038` with the affected reports named. Whether the report publishes is decided by that report's own quality gate, not by the SLO breach. The two are separate decisions and conflating them is a common design error.

---

## 6. Change management for contracts

| Change type | Minimum notice | Approval | Verification |
|---|---|---|---|
| Additive column | 10 business days | P-12 delegate | Contract test suite passes |
| Column type change | 20 business days | P-12 and every consuming persona | Full regression on consuming reports |
| Column semantic change | 40 business days | P-12, the metric owner, and P-14 non-objection | Restatement assessment under `BR-DQ-009` |
| Column removal | 40 business days | P-12 and every consuming persona | Consumers migrated first, verified, then removed |
| Grain change | 60 business days | P-12, P-01 or P-06 as applicable, P-14 non-objection | Treated as a new contract with parallel run |
| Window change | 20 business days | P-12 and every consuming persona whose latency class is affected | Latency SLO re-derived and re-agreed |

An unannounced schema change is a contract breach in its own right, counted against the tolerance in section 2, whether or not it broke anything. The platform detects it at ingestion and rejects the delivery.

---

## 7. Contract testing

Every contract carries an executable test suite, run at ingestion, before promotion to Silver.

| Test class | What it asserts |
|---|---|
| Structural | Expected columns present, types match, no unannounced additions |
| Volumetric | Row count within the expected band for the day of week and month position. A 40 % deviation is investigated before promotion |
| Referential | `BR-DQ-002` on every declared foreign key in the payload |
| Domain | `BR-DQ-005` on every constrained column |
| Completeness | `BR-DQ-006` at the criticality threshold for each column |
| Temporal | No future-dated business dates; no `as_of_date` older than the prior successful delivery |
| Reconciliation | The applicable rows of the `BR-DQ-004` set |
| Idempotence | Re-delivering the same payload produces no change |

Test results are published to `RPT-038` on every run, whether they pass or fail. A contract with no failures recorded in a quarter is audited to confirm its tests actually execute, because a permanently green test is more often broken than perfect.
