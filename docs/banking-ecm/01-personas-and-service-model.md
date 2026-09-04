# 01 — Personas and Service Model

**Document ID:** OAFG-BSR-2026-01 · **Version:** 1.0 · **Owner:** Head of Business Analysis · **Approver:** Group Executive Committee

---

## 1. How to read a persona

Each persona is specified with the same eight fields. This is deliberate: a persona that cannot state its decision rights and its failure mode is a job title, not a persona, and cannot be designed for.

| Field | What it establishes |
|---|---|
| **Decision rights** | What this person is accountable for deciding. Reports exist to support decisions, not to inform generally. |
| **Jobs to be done** | The recurring work, expressed as outcomes rather than activities |
| **Cadence** | When the work happens, which sets the latency budget |
| **Questions asked** | The literal questions. These become report acceptance tests. |
| **Entitlement class** | `ENT-n` from [06](./06-governance-security-and-controls.md), which fixes what data is visible |
| **Report portfolio** | The `RPT-nnn` specifications this persona consumes, with primary ownership marked |
| **Latency tolerance** | The maximum staleness at which the persona's decision is still safe |
| **Failure mode** | What goes wrong when the platform serves this persona badly. This is the real requirement. |

---

## 2. Persona index

| ID | Persona | Division | Entitlement | Primary reports |
|---|---|---|---|---|
| P-01 | Group Chief Risk Officer | Risk | `ENT-1` | RPT-001, RPT-002, RPT-016 |
| P-02 | Head of Credit Portfolio Management | Risk / Wholesale | `ENT-2` | RPT-003, RPT-004, RPT-005 |
| P-03 | Credit Risk Analyst, Wholesale | Risk / Wholesale | `ENT-2` | RPT-005, RPT-006, RPT-007 |
| P-04 | Group Treasurer and Head of ALM | Treasury | `ENT-5` | RPT-012, RPT-013, RPT-014, RPT-015 |
| P-05 | Regulatory Reporting Manager | Finance | `ENT-5` | RPT-009, RPT-010, RPT-011 |
| P-06 | Chief Financial Officer / Group Controller | Finance | `ENT-5` | RPT-028, RPT-029, RPT-030 |
| P-07 | Chief Compliance Officer, Financial Crime | Compliance | `ENT-3` | RPT-021, RPT-022, RPT-023 |
| P-08 | AML Investigations Team Lead | Compliance | `ENT-3` | RPT-020, RPT-022 |
| P-09 | Fraud Operations Manager | Operations | `ENT-3` | RPT-024, RPT-025 |
| P-10 | Head of Retail and Digital Channels | Retail | `ENT-4` | RPT-032, RPT-033 |
| P-11 | Corporate Relationship Manager | Wholesale | `ENT-4` | RPT-031, RPT-006, RPT-007 |
| P-12 | Chief Data Officer and Data Stewards | Corporate | `ENT-7` | RPT-038, RPT-039 |
| P-13 | Head of Model Risk Management | Risk | `ENT-2` | RPT-034, RPT-035 |
| P-14 | Chief Audit Executive | Internal Audit | `ENT-6` | RPT-036, RPT-037 |

Delivery-side personas (D-01 to D-03) are specified in section 8. They consume the platform's operational telemetry rather than its business reporting.

---

## 3. Risk personas

### P-01 — Group Chief Risk Officer

**Profile.** Accountable to the Board Risk Committee for the group's aggregate risk position across credit, market, liquidity, operational, financial crime and model risk. Reads at aggregate level, drills only when a number surprises them. Has no time and no tolerance for a number they cannot trust.

**Decision rights**
- Approves the Group Risk Appetite Statement and every limit that sits directly under it
- Declares a risk appetite breach and the escalation it triggers
- Signs the risk sections of the Board pack, Pillar 3 disclosure and the CCAR submission
- Can halt origination in a portfolio segment

**Jobs to be done**
1. Know, before the Board does, where the group sits against every appetite metric
2. Explain any month-on-month movement larger than the metric's tolerance, attributed by cause
3. Answer a supervisor's ad-hoc aggregation request within the supervisor's deadline
4. Confirm that risk numbers reconcile to the numbers Finance publishes

**Cadence.** Monthly Board Risk Committee. Weekly executive risk forum. Ad hoc during stress.

**Questions asked**
- "Which appetite metrics are amber or red this month, and which of those were green last month?"
- "Our stage 2 balance moved USD 340 million. How much of that is new lending, how much is migration, how much is FX?"
- "What is our single largest connected-group exposure as a percentage of tier 1, at group level, today?"
- "If the severely adverse scenario ran on today's book rather than the December book, where does CET1 land?"
- "Does the credit exposure in this pack equal the credit exposure we filed on the Y-14?"

**Entitlement.** `ENT-1`. Aggregate and portfolio level. No customer PII. May drill to counterparty name for exposures above the large-exposure threshold only, because that is a named-counterparty decision they are accountable for.

**Report portfolio.** Owns RPT-001, RPT-002, RPT-016. Consumes RPT-003, RPT-004, RPT-012, RPT-017, RPT-018, RPT-034, RPT-037.

**Latency tolerance.** Appetite metrics T+1 business day. Board pack metrics T+4 business days from month end. Ad-hoc aggregation within 4 hours, which is objective O3.

**Failure mode.** The CRO presents a number to the Board, a Board member asks what drives it, and the answer is "we will come back to you". Every design decision for P-01 optimises for the drill-down being present before the question is asked, not for the headline being pretty.

---

### P-02 — Head of Credit Portfolio Management

**Profile.** Owns the wholesale credit portfolio's shape: concentration, quality migration, impairment adequacy and origination standards. Works in exposures and cohorts, not individual deals, except when a single name is large enough to matter on its own.

**Decision rights**
- Sets and reallocates sub-limits within the CRO's approved appetite
- Approves the quarterly ECL model overlay and post-model adjustment
- Approves watchlist entry and exit for names above USD 25 million exposure
- Recommends portfolio-level origination restrictions to P-01

**Jobs to be done**
1. Keep concentration inside limits across counterparty, industry, geography, product and collateral dimensions simultaneously
2. Detect quality deterioration early enough to act, which means before it reaches stage 3
3. Defend the ECL number to Finance, to Audit and to the supervisor
4. Prove that origination is behaving the way the approved credit policy says it should

**Cadence.** Weekly portfolio review. Monthly impairment committee. Quarterly deep dive with P-01 and P-06.

**Questions asked**
- "Show me every industry where our exposure grew more than 10 % this quarter while the average rating deteriorated."
- "Which names moved from stage 1 to stage 2 this month, why, and what is the ECL impact of each?"
- "What is our HHI on the commercial real estate book by geography, and how does that compare to the limit?"
- "What proportion of our stage 2 population is there because of the 30-days-past-due backstop rather than a genuine SICR signal?"
- "If I exclude the top 20 names, does the portfolio still look like it did last quarter?"

**Entitlement.** `ENT-2`. Full counterparty detail within the wholesale perimeter. Party identifiers masked except legal name and internal identifiers. No retail customer detail.

**Report portfolio.** Owns RPT-003, RPT-004, RPT-005. Consumes RPT-006, RPT-007, RPT-008, RPT-016, RPT-018, RPT-019.

**Latency tolerance.** Concentration T+1. Impairment T+3 business days from month end. Watchlist and early warning T+1, because a day matters when a name is deteriorating.

**Failure mode.** A name defaults and the post-mortem shows the signals were all present in the platform but split across four reports that nobody read together. The design answer is that early warning is one report with every signal on it, not five reports each with one signal.

---

### P-03 — Credit Risk Analyst, Wholesale

**Profile.** Does the actual analysis. Reads at counterparty and facility level, builds the evidence packs that P-02 presents. Spends most of their time reconciling, and resents every minute of it.

**Decision rights**
- Proposes rating overrides, which require committee approval under `BR-CRR-014`
- Proposes stage overrides, which require approval under `BR-IMP-011`
- Owns the accuracy of the analysis pack they produce
- Cannot approve their own proposal, ever

**Jobs to be done**
1. Assemble a complete counterparty view: exposure, rating, collateral, covenants, payment behaviour, group structure
2. Test whether a stage or rating movement is genuine or a data artefact
3. Prepare committee papers with an audit trail sufficient for Internal Audit
4. Answer P-02's questions without a two-day turnaround

**Cadence.** Daily. Peaks in the five business days after month end.

**Questions asked**
- "Give me everything on this counterparty and every entity in its relationship hierarchy, in one place."
- "Why does the exposure in the risk system differ from the drawn balance in the loan system for this facility?"
- "Which covenants on my portfolio are tested this month, and which are within 10 % of their threshold?"
- "Show me the collateral supporting this exposure, its latest valuation, its haircut and whether the valuation is stale."
- "What was this counterparty's rating and stage at each of the last eight quarter ends, and what changed it?"

**Entitlement.** `ENT-2`, scoped by assigned portfolio. Full facility and covenant detail. Party PII masked.

**Report portfolio.** Owns RPT-005, RPT-006, RPT-007. Consumes RPT-003, RPT-004, RPT-018, RPT-019, RPT-031.

**Latency tolerance.** T+1 for portfolio views. Intraday for the counterparty deep-dive view, which must reflect any rating or limit change made the same day.

**Failure mode.** The analyst rebuilds the same reconciliation in a spreadsheet every month because the platform gives them two numbers and no explanation of the difference. Every variance the platform can attribute, it must attribute, in the report, without being asked.

---

### P-13 — Head of Model Risk Management

**Profile.** Independent second-line function. Validates that the models producing PD, LGD, EAD, ECL, VaR, fraud scores and AML scores are fit for use, and that they are actually used the way they were approved to be used.

**Decision rights**
- Approves or withholds approval for a model to be used in regulatory capital or financial reporting
- Assigns model risk ratings and sets validation frequency
- Declares a model out of tolerance, which suspends its use for capital
- Approves the treatment of model overrides

**Jobs to be done**
1. Maintain a complete, reconciled model inventory with no undocumented models in production use
2. Track validation currency and escalate overdue validations before they become a supervisory finding
3. Monitor live model performance against the thresholds set at validation
4. Quantify how much of the reported outcome is model output and how much is human override

**Cadence.** Monthly inventory and performance review. Quarterly validation committee. Annual full revalidation cycle.

**Questions asked**
- "Which models used in RWA or ECL have a validation date older than their approved frequency?"
- "What is the override rate on the wholesale PD model this quarter, in which direction, and by which analysts?"
- "Has the Gini coefficient on this model degraded beyond the threshold set at approval?"
- "Which models failed their most recent backtest, and are any of them still feeding a regulatory number?"
- "Show me every reported metric whose value depends on a model with a red model risk rating."

**Entitlement.** `ENT-2`. Full model metadata, performance statistics and override records. Aggregate exposure only, since MRM validates models rather than positions.

**Report portfolio.** Owns RPT-034, RPT-035. Consumes RPT-004, RPT-005, RPT-016, RPT-025, RPT-038.

**Latency tolerance.** Monthly for inventory and performance. Immediate for a backtest failure on a capital-feeding model, which is an alert rather than a report.

**Failure mode.** A supervisor asks which regulatory numbers depend on a model whose validation lapsed, and the answer requires a manual exercise. The platform must carry the model-to-metric dependency as a first-class relationship, which is why `MET-047` and `MET-048` exist.

---

## 4. Treasury and finance personas

### P-04 — Group Treasurer and Head of ALM

**Profile.** Owns liquidity, funding, capital adequacy and interest rate risk in the banking book. The only persona whose primary report has a hard external deadline every single business day.

**Decision rights**
- Executes funding and liquidity actions inside ALCO-approved parameters
- Approves FTP curve construction and rate publication
- Declares a liquidity early-warning trigger
- Recommends capital actions to the ALCO and the Board

**Jobs to be done**
1. Prove LCR and NSFR compliance daily and monthly, at every required consolidation level and in every material currency
2. Know intraday liquidity position and peak usage before it becomes a settlement problem
3. Allocate funding cost to the businesses in a way they will accept and can act on
4. Project capital and liquidity under stress and under the funding plan

**Cadence.** Daily by 09:00 local for liquidity. Monthly ALCO. Quarterly capital planning.

**Questions asked**
- "What is the group LCR as at close of business yesterday, and which entity or currency is the binding constraint?"
- "Which HQLA positions became encumbered overnight, and what did that do to the buffer?"
- "Under the severe stress scenario, on which day does the survival horizon break?"
- "What is the FTP-adjusted contribution margin by line of business, and which product is being subsidised?"
- "What is our projected CET1 in each of the next three years given the current capital plan?"

**Entitlement.** `ENT-5`. Full treasury, ledger and account balance data. Counterparty names for interbank and repo counterparties. No retail PII.

**Report portfolio.** Owns RPT-012, RPT-013, RPT-014, RPT-015. Consumes RPT-009, RPT-016, RPT-027, RPT-030.

**Latency tolerance.** LCR by 09:00 on T+1, absolutely. Intraday liquidity within 30 minutes of the underlying movement. Monthly measures T+3.

**Failure mode.** The 09:00 LCR is late or wrong. This is the single hardest latency requirement in the specification and drives `NFR-004` and the entire late-arrival design in `BR-DQ-012`.

---

### P-05 — Regulatory Reporting Manager

**Profile.** Produces the regulatory submissions. Cares about one thing above all others: that what was submitted can be reproduced, explained and defended, months or years later.

**Decision rights**
- Signs the submission as complete and accurate, personally
- Determines whether a difference requires a resubmission or a prospective correction
- Approves the mapping from ECM attributes to regulatory line items
- Can refuse to submit on data quality grounds

**Jobs to be done**
1. Produce each return from a certified, frozen extract with full lineage to source
2. Reconcile every return to the general ledger and to the risk system, and explain every difference
3. Reproduce any prior submission exactly, on demand, for a supervisory question or an audit
4. Track and evidence the resolution of every validation rule failure before submission

**Cadence.** Daily (FR 2052a), monthly (AnaCredit, FR Y-14M), quarterly (Call Report, FR Y-9C, COREP, FINREP, FR Y-14Q), annual (FR Y-14A).

**Questions asked**
- "Does the total credit exposure on this return tie to the risk system and to the ledger? Show me the bridge."
- "Reproduce the Q3 submission exactly as filed, including the FX rates and the model versions used."
- "Which validation rules failed this cycle, who cleared them, and on what evidence?"
- "What changed between the number we filed last quarter and the number the same query returns today?"
- "Which loans are in the AnaCredit population this month that were not last month, and why?"

**Entitlement.** `ENT-5`. Full data at submission grain, including loan-level detail for AnaCredit and FR Y-14. Party identifiers visible where the return requires them, masked otherwise.

**Report portfolio.** Owns RPT-009, RPT-010, RPT-011. Consumes RPT-004, RPT-012, RPT-028, RPT-029, RPT-038.

**Latency tolerance.** Aligned to each return's regulatory deadline minus a mandatory four-business-day internal review window.

**Failure mode.** A supervisor asks why a number changed and the platform can only show today's answer. Everything about `ARCH-05`, `BR-REG-004` and the bitemporal design in [00, section 6](./00-programme-charter-and-scope.md#6-bitemporality) exists for this persona.

---

### P-06 — Chief Financial Officer and Group Financial Controller

**Profile.** Treated as one persona with two altitudes. The CFO consumes segment results and the group position. The Controller owns the close, the reconciliations and the control attestations that make those results supportable.

**Decision rights**
- Signs the group financial statements
- Approves the close calendar and declares the close complete
- Approves manual journal entries above delegated thresholds
- Owns the SOX control environment over financial reporting

**Jobs to be done**
1. Complete the close in six working days with every reconciliation cleared or explained
2. Ensure subledger and general ledger agree, at every legal entity, in every currency
3. Report segment profitability on an FTP-adjusted, risk-adjusted basis
4. Evidence that every SOX key control operated, with no exceptions unremediated

**Cadence.** Daily during close. Monthly reporting. Quarterly external reporting.

**Questions asked**
- "Which close tasks are late, who owns them, and what is the critical path to sign-off?"
- "What is the subledger-to-GL variance by entity and by subledger, and which ones exceed materiality?"
- "How many manual journals were posted this period, by whom, above what value, and were they all approved?"
- "What is the ECL charge in the P&L, and does it agree to the risk system's provision movement?"
- "Show me segment return on equity after FTP and after capital allocation."

**Entitlement.** `ENT-5`. Full ledger, full segment results. No customer-level detail beyond what a material single exposure requires.

**Report portfolio.** Owns RPT-028, RPT-029, RPT-030. Consumes RPT-004, RPT-015, RPT-009, RPT-037.

**Latency tolerance.** Intraday during close, refreshed at least hourly. Monthly results T+6 working days.

**Failure mode.** Close slips because a reconciliation break is found on day five that was visible in the data on day one. The close control tower report exists to move discovery earlier, which is why `RPT-028` refreshes hourly rather than daily.

---

## 5. Financial crime and fraud personas

### P-07 — Chief Compliance Officer, Financial Crime

**Profile.** Accountable to the Board and to regulators for the effectiveness of the financial crime programme. Judged not on how many alerts were generated but on whether the programme actually catches things and meets its filing obligations.

**Decision rights**
- Approves the customer risk rating methodology and the enhanced due diligence triggers
- Approves SAR filing decisions above the delegated threshold
- Declares a programme deficiency and owns its remediation
- Approves monitoring rule changes, additions and retirements

**Jobs to be done**
1. Evidence that every filing obligation was met inside its statutory deadline, with no exceptions
2. Keep the periodic KYC review population current, with high-risk customers never overdue
3. Demonstrate monitoring coverage across products, channels and typologies, with no gaps
4. Show that alert volumes are being worked, not just generated

**Cadence.** Daily filing-deadline check. Weekly programme review. Monthly Board Financial Crime Committee.

**Questions asked**
- "Is any SAR or CTR approaching or past its statutory deadline right now?"
- "How many high-risk customers have an overdue periodic review, and how long overdue?"
- "Which monitoring rules have produced no true positives in six months, and which typologies have no rule coverage at all?"
- "What is our sanctions screening false-positive rate by list and by matching algorithm?"
- "Which customers were rated high risk this month who were not last month, and what triggered it?"

**Entitlement.** `ENT-3`. Full customer PII, full alert and case detail, SAR content. This is the only entitlement class with SAR visibility, enforced under `CTL-011`.

**Report portfolio.** Owns RPT-021, RPT-022, RPT-023. Consumes RPT-020, RPT-024, RPT-033, RPT-037.

**Latency tolerance.** Filing deadlines refreshed at least every 4 hours, because a missed statutory deadline is a regulatory breach that cannot be undone. Everything else daily.

**Failure mode.** A statutory filing deadline is missed. `RPT-021` is designed as a countdown, not a status list, for exactly this reason.

---

### P-08 — AML Investigations Team Lead

**Profile.** Runs the alert and case queues. Manages a team whose productivity, quality and SLA compliance are all measured, and who need context that is currently spread across six systems.

**Decision rights**
- Assigns and reassigns alerts and cases
- Approves alert closure as a false positive below the escalation threshold
- Escalates to case and recommends SAR filing
- Sets team-level quality sampling

**Jobs to be done**
1. Keep every alert and case inside its SLA
2. Give each investigator the full subject context on one screen, so that investigation time goes into judgement rather than data gathering
3. Balance the queue across analysts by complexity, not just count
4. Feed genuine false-positive patterns back to tuning

**Cadence.** Continuous. Queue reviewed at least twice daily.

**Questions asked**
- "Which alerts breach SLA today, and which breach in the next 24 hours?"
- "For this subject, show every account, every related party, every payment counterparty and every prior alert."
- "What is the alert-to-case conversion rate by rule, and which rules are pure noise?"
- "Which investigators have ageing cases, and is that workload or capability?"
- "Has this subject appeared in a fraud case as well as an AML alert?"

**Entitlement.** `ENT-3`, scoped to assigned queue for investigators and to full team for the lead.

**Report portfolio.** Owns RPT-020. Consumes RPT-021, RPT-022, RPT-023, RPT-024.

**Latency tolerance.** Alert data within 15 minutes of generation. Subject context intraday, refreshed at least hourly.

**Failure mode.** An investigator closes an alert as a false positive because the context that would have made it a true positive lived in a system they do not have open. The cross-domain subject view is the entire point of building this on a single model.

---

### P-09 — Fraud Operations Manager

**Profile.** Runs real-time and near-real-time fraud detection operations. Measured on loss, on detection performance, and on the customer friction that detection causes.

**Decision rights**
- Adjusts detection rule thresholds inside approved bounds
- Approves rule deployment and retirement
- Sets case triage priority
- Approves customer reimbursement below delegated limits

**Jobs to be done**
1. Keep fraud losses within appetite while keeping false-positive friction acceptable
2. Detect emerging typologies before they scale
3. Prove rule performance so that tuning decisions are evidence-based
4. Recover losses and manage chargeback disputes inside network deadlines

**Cadence.** Intraday, continuously. Daily operations review. Weekly rule tuning forum.

**Questions asked**
- "What is today's fraud loss by channel and typology against the daily appetite?"
- "Which rules fired most in the last 24 hours, and what was their precision?"
- "Are we seeing a device, IP or merchant cluster across otherwise unrelated alerts?"
- "What is our chargeback ratio by merchant, and which merchants are approaching network thresholds?"
- "How much of last month's gross loss did we recover, and how much is still open?"

**Entitlement.** `ENT-3`. Full fraud alert and case detail including device, IP and geolocation. Card numbers permanently truncated to last four digits at source.

**Report portfolio.** Owns RPT-024, RPT-025. Consumes RPT-020, RPT-026, RPT-032, RPT-037.

**Latency tolerance.** Alert and loss data within 5 minutes. Rule performance daily. Network cluster detection hourly.

**Failure mode.** A fraud ring operates for three weeks because each alert looked isolated. `fraud.network_link`, `fraud.fraud_ring` and `fraud.device_fingerprint` exist in the model; the requirement is that the reporting actually traverses them.

---

## 6. Front-line and customer personas

### P-10 — Head of Retail and Digital Channels

**Profile.** Owns the retail customer experience across branch, ATM, contact centre, mobile and web. Commercially accountable, but increasingly judged on conduct outcomes rather than volume.

**Decision rights**
- Prioritises the digital roadmap and channel investment
- Sets channel service level targets
- Owns complaint handling standards and root-cause remediation
- Approves campaign targeting rules

**Jobs to be done**
1. Keep channels available and within service levels
2. Understand where customer journeys break, and fix the cause rather than the symptom
3. Detect conduct risk early through complaint patterns rather than after a regulatory finding
4. Grow the book without degrading credit quality or conduct outcomes

**Cadence.** Daily operations. Weekly channel performance. Monthly conduct review.

**Questions asked**
- "Which channels breached their service level yesterday, for how long, and how many customers were affected?"
- "Where in the onboarding journey do applicants abandon, and has that changed?"
- "Which complaint themes are growing, and do any of them concentrate in one product or one branch?"
- "What is our digital onboarding cycle time, end to end, and which step is the constraint?"
- "Are customers acquired through digital channels performing differently on credit quality?"

**Entitlement.** `ENT-4`. Retail aggregate and journey-level data. Customer-level detail only for complaint cases they own. PII masked throughout.

**Report portfolio.** Owns RPT-032, RPT-033. Consumes RPT-008, RPT-024, RPT-031, RPT-037.

**Latency tolerance.** Channel availability within 5 minutes. Journey and complaint data daily.

**Failure mode.** A conduct issue is identified by the regulator from complaint data before it is identified internally. `RPT-033` is built around theme clustering and trend, not around case counts.

---

### P-11 — Corporate Relationship Manager

**Profile.** Owns a portfolio of corporate clients commercially. Needs the full client picture before every conversation, and needs to know about a problem before the client mentions it.

**Decision rights**
- Owns the client relationship plan and pricing proposals within approved grids
- Recommends limit increases, which they cannot approve
- Flags client circumstances that should influence rating or watchlist status
- Cannot alter a risk rating, a stage, or a limit

**Jobs to be done**
1. Walk into a client meeting knowing every position, every covenant, every open service issue and every risk flag
2. Know which of their clients face a covenant test, a maturity or a review in the next 90 days
3. Understand relationship profitability after funding cost and capital
4. Spot cross-sell opportunity without tripping suitability or conduct rules

**Cadence.** Daily client preparation. Weekly pipeline. Quarterly relationship review.

**Questions asked**
- "Show me everything on this client group: exposures, collateral, covenants, payments, service issues, risk flags."
- "Which of my clients has a covenant test or a facility maturity in the next 90 days?"
- "What is this relationship worth after FTP and after allocated capital?"
- "Has anything changed on my portfolio in the last week that I have not been told about?"
- "Which of my clients has an overdue KYC review that will block their next drawdown?"

**Entitlement.** `ENT-4`, restricted by `channel.rm_client_assignment` and `account.rm_account_assignment` to their own portfolio. Row-level security is enforced in Unity Catalog, not in the report tool. Sees client PII for assigned clients only, and never sees AML alert or SAR existence, enforced under `CTL-011`.

**Report portfolio.** Owns RPT-031. Consumes RPT-006, RPT-007, RPT-008.

**Latency tolerance.** T+1 for the client view. Same-day for covenant, limit and rating changes on their portfolio.

**Failure mode.** An RM asks a client for new business on the same day the bank internally downgrades them, because nobody told the RM. Equally bad: an RM learns that a client is under AML investigation, which is a tipping-off offence. Both failure modes are entitlement design problems, and both are solved in `CTL-011`.

---

## 7. Control and governance personas

### P-12 — Chief Data Officer and Data Stewards

**Profile.** Treated as one persona with two altitudes. The CDO is accountable for BCBS 239 compliance and the data control environment. Domain stewards are accountable for the quality of specific critical data elements.

**Decision rights**
- Certifies a metric, a dimension or a dataset as fit for regulatory or board use
- Assigns and enforces critical data element ownership
- Blocks a report from publication on data quality grounds
- Approves changes to certified metric definitions jointly with the business owner

**Jobs to be done**
1. Maintain a complete critical data element inventory with a named owner and a live quality score for each
2. Evidence end-to-end lineage from every board-reported and regulatory-submitted figure back to source
3. Detect quality degradation before a consumer does
4. Prove BCBS 239 principle compliance to a supervisor with artefacts rather than assertions

**Cadence.** Daily quality monitoring. Monthly steward forum. Quarterly BCBS 239 attestation.

**Questions asked**
- "Which critical data elements failed their quality thresholds today, and which reports consume them?"
- "For this number in the Board pack, show me every table, column and transformation between it and the source system."
- "Which certified metrics have been changed in the last quarter, by whom, with what approval?"
- "Which datasets have no named steward?"
- "If this source feed fails tonight, which reports are affected and which of them have regulatory deadlines?"

**Entitlement.** `ENT-7`. Full metadata, lineage, quality results and access logs. Sees no business data values beyond what quality profiling requires, and never sees unmasked PII.

**Report portfolio.** Owns RPT-038, RPT-039. Consumes every report's quality header.

**Latency tolerance.** Quality results within one pipeline cycle of the data they measure. Lineage always current with deployed code.

**Failure mode.** A supervisor asks for lineage on a specific figure and the response is a hand-drawn diagram. Lineage must be generated from the deployed pipeline, not maintained as documentation.

---

### P-14 — Chief Audit Executive

**Profile.** Third line. Reads everything, changes nothing. Needs independent access precisely because they are testing whether the first and second lines are telling the truth.

**Decision rights**
- Sets the audit plan and the risk-based universe
- Rates findings and sets remediation deadlines
- Validates that a management action actually closed the risk
- Escalates unremediated findings to the Audit Committee

**Jobs to be done**
1. Test controls against evidence rather than against management's assertion
2. Track every open finding and management action to closure, with ageing
3. Identify themes across findings that indicate a systemic control weakness
4. Report independently to the Audit Committee on the state of remediation

**Cadence.** Continuous audit monitoring. Monthly issue tracking. Quarterly Audit Committee.

**Questions asked**
- "Which management actions are past due, by how long, and who owns each?"
- "Which findings have been closed by management but not yet validated by audit?"
- "Do any findings cluster on the same root cause across different business units?"
- "Show me the change history and approvals for this certified metric over the last year."
- "Which risk appetite breaches occurred, and did each one follow the escalation the appetite statement requires?"

**Entitlement.** `ENT-6`. Read-only access across all domains, including PII where an audit test requires it, with every access logged and reported to the CDO. No write access anywhere, no ability to alter a report definition.

**Report portfolio.** Owns RPT-036, RPT-037. Consumes every report, by design.

**Latency tolerance.** Issue tracking daily. Everything else at the cadence of the report being tested.

**Failure mode.** Audit cannot independently verify a number because they can only see the same curated view management sees. `ENT-6` therefore grants Silver-layer access, not just Gold.

---

## 8. Delivery personas

These personas do not consume business reporting. They are specified because [08](./08-non-functional-requirements.md) is written for them.

| ID | Persona | Needs from the platform | Primary telemetry |
|---|---|---|---|
| D-01 | Data Engineer | Deterministic reruns, clear contract violations, backfill without side effects | Pipeline run history, contract validation results, `DC-nnn` breach log |
| D-02 | Platform Site Reliability Engineer | Capacity headroom, cost attribution, failure blast radius | Warehouse utilisation, query concurrency, job SLO burn rate |
| D-03 | BI Developer | Stable certified metrics, documented grain, no silent schema change | Semantic layer contract, deprecation notices, schema evolution log |

---

## 9. Persona prompts for Copilot Spaces

These prompts configure a Copilot Space to answer in the voice and at the altitude of a given persona, grounded in this document set. Each assumes the Space has been loaded with the sources listed in [README section 6](./README.md#6-using-this-set-with-copilot-spaces).

**P-01, Group Chief Risk Officer**
> Answer as a group chief risk officer preparing for a Board Risk Committee. Lead with the position against risk appetite, then the movement since last period attributed by cause, then what you would do about it. Cite the certified metric identifier (`MET-nnn`) for every number. If a number cannot be produced from the certified layer, say so explicitly rather than approximating. Never quote a customer name unless the exposure exceeds the large exposure threshold.

**P-02, Head of Credit Portfolio Management**
> Answer as a wholesale credit portfolio head. Work in exposures, cohorts and migrations, not individual transactions. Always separate a movement into new business, migration, repayment and foreign exchange. When discussing impairment, state the IFRS 9 stage, the SICR trigger that caused it, and the source columns in `risk.risk_ecl_provision`. Flag when the 30-days-past-due backstop rather than a genuine risk signal is driving stage 2.

**P-04, Group Treasurer**
> Answer as a group treasurer accountable for daily LCR delivery by 09:00. State the consolidation level and currency for every ratio. Identify the binding constraint, not just the headline ratio. Reference `treasury.liquidity_ratio` and `risk.liquidity_metric` columns explicitly. Treat any answer that cannot be produced by the deadline as a failure regardless of its accuracy.

**P-05, Regulatory Reporting Manager**
> Answer as a regulatory reporting manager who must personally sign the submission. For every figure, state its source, its as-of date, its knowledge date, and whether it comes from a frozen submission snapshot or a current view. Never present a current-view number as if it were what was filed. Always offer the reconciliation bridge to the general ledger and to the risk system.

**P-07, Chief Compliance Officer, Financial Crime**
> Answer as a chief compliance officer for financial crime. Statutory deadlines are absolute; lead with anything at risk of breach. Never disclose or imply the existence of a suspicious activity report to anyone outside entitlement class `ENT-3`. Distinguish between alert volume, alert quality and programme coverage, and do not let a high alert count be presented as effectiveness.

**P-11, Corporate Relationship Manager**
> Answer as a corporate relationship manager preparing for a client meeting. Cover exposure, collateral, covenants, upcoming maturities, service issues and open onboarding items. You are restricted to your own assigned portfolio. You must never surface, hint at, or speculate about anti-money-laundering alerts, cases or filings, because doing so is a tipping-off offence. If asked about them, state that the information is outside your entitlement.

**P-12, Chief Data Officer**
> Answer as a chief data officer accountable for BCBS 239. For any figure, be able to state its lineage, its owning steward, its current quality score and every report that consumes it. Prefer evidence over assertion. When a control is described, name the control identifier (`CTL-nnn`) and how its operation is evidenced.

**P-14, Chief Audit Executive**
> Answer as a chief audit executive. Test assertions rather than accepting them. For every control described, ask what evidence proves it operated, over what period, and who reviewed the evidence. Track findings and management actions by age and by root cause theme. You have read access to everything and change rights to nothing.
