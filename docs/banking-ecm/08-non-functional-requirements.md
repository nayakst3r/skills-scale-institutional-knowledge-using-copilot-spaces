# 08 — Non-Functional Requirements

**Document ID:** OAFG-BSR-2026-08 · **Version:** 1.0 · **Owner:** Head of Data Platform Engineering · **Approvers:** P-12, and P-04 for `NFR-004`

---

## 1. How these are measured

Every requirement here states a measurement method and a measurement point. A performance requirement without a stated percentile and a stated load is not testable and is not a requirement.

| Convention | Meaning |
|---|---|
| p50, p95, p99 | Percentile of the measured distribution over a rolling 30-day window |
| Measured at | The point of measurement, which is always the consumer's experience, not the server's |
| Under load | The concurrency stated in `NFR-010`, not single-user |
| At scale | The volumetrics in [00, section 1.3](./00-programme-charter-and-scope.md#13-scale-assumptions) |

---

## 2. Latency

| ID | Requirement | Target | Measured at |
|---|---|---|---|
| `NFR-001` | Streaming ingestion lag, payments and channels | p95 ≤ 2 minutes, p99 ≤ 5 minutes | Source event timestamp to Silver availability |
| `NFR-002` | Streaming ingestion lag, fraud and AML alerts | p95 ≤ 3 minutes, p99 ≤ 10 minutes | Alert generation to Silver availability |
| `NFR-003` | Batch Silver-to-Gold build, daily cycle | ≤ 90 minutes at scale | Contract completion to Gold availability |
| `NFR-004` | **RPT-012 availability** | Available by 09:00 local, every business day, 100 % of the time | Report render complete, measured from the consumer's browser |
| `NFR-005` | Dashboard first render, standard reports | p95 ≤ 3 seconds | Consumer browser, cold cache |
| `NFR-006` | **RPT-020 subject context panel** | p95 ≤ 5 seconds for a subject with 40 related parties and 200,000 transactions | Consumer browser |
| `NFR-007` | Drill-down from an aggregate to detail | p95 ≤ 5 seconds | Consumer browser |
| `NFR-008` | Ad-hoc aggregation over the certified layer | p95 ≤ 4 hours end to end, including analyst formulation, per `BR-REG-008` | Request logged to answer delivered |
| `NFR-009` | Lineage impact analysis query | p95 ≤ 10 seconds | Query response |

`NFR-004` is the platform's defining constraint. Its four-and-a-half-hour margin from the `DC-012` delivery window at 04:30 exists so that a single failed run can be retried twice and still make the deadline. Any design change that erodes that margin requires P-04's approval.

## 3. Throughput and concurrency

| ID | Requirement | Target |
|---|---|---|
| `NFR-010` | Concurrent named report consumers | 2,400 sustained, 3,600 at peak close, with no degradation beyond one latency band |
| `NFR-011` | Concurrent ad-hoc analyst queries | 120 sustained without affecting scheduled report SLOs |
| `NFR-012` | Payment event ingestion | 3,000 events per second sustained, 12,000 per second peak |
| `NFR-013` | Channel session event ingestion | 8,000 events per second sustained |
| `NFR-014` | Month-end batch window | The full monthly Gold build completes within 6 hours, leaving the `RPT-004` T+3 deadline achievable with a full rerun |
| `NFR-015` | Workload isolation | Ad-hoc analytical workloads can never delay a scheduled regulatory report. Separate compute, enforced, not advisory |

## 4. Scale and growth

| ID | Requirement |
|---|---|
| `NFR-020` | The platform operates at the [00, section 1.3](./00-programme-charter-and-scope.md#13-scale-assumptions) volumetrics with 36 months of growth headroom at the stated growth rates, without re-architecture |
| `NFR-021` | Adding a legal entity requires configuration, not code. Adding a jurisdiction requires configuration plus its regulatory mapping, not a new pipeline |
| `NFR-022` | The largest single table, `account.account_transaction` at 5.8 billion rows, supports point lookup by account and date range scan by account within `NFR-007` |
| `NFR-023` | A full historical rebuild of Gold from Silver completes within 72 hours, which is the disaster recovery constraint in `NFR-042` |
| `NFR-024` | Retention growth is planned to the [06, section 6](./06-governance-security-and-controls.md#6-retention) schedule, with storage tiering that does not compromise the reproducibility requirement in `NFR-030` |

## 5. Correctness and reproducibility

| ID | Requirement |
|---|---|
| `NFR-030` | Any Gold table is deterministically rebuildable from Silver for any historical `as_of_date`, producing bit-identical output, per `ARCH-04` |
| `NFR-031` | Any frozen submission snapshot reproduces exactly, per `BR-REG-004`. A reproduction difference is severity 1 |
| `NFR-032` | Pipelines are idempotent. Re-running any job with the same inputs produces no change and no duplicate |
| `NFR-033` | Late-arriving data is processed without reprocessing unaffected partitions, so that `BR-DQ-012` handling is fast enough to be useful |
| `NFR-034` | Every computation records the code version, the model versions and the reference data version it used |
| `NFR-035` | Floating-point arithmetic is not used for monetary amounts anywhere. All money is `DECIMAL(18,2)`, per `MAT-02` |

## 6. Availability and recovery

| ID | Requirement | Target |
|---|---|---|
| `NFR-040` | Platform availability during business hours | 99.9 % monthly, measured as successful report renders over attempted |
| `NFR-041` | Recovery time objective | 4 hours for reporting, 1 hour for streaming ingestion |
| `NFR-042` | Recovery point objective | 15 minutes for streaming, one completed batch cycle for batch |
| `NFR-043` | Regional failover | Tested twice yearly with a real failover, not a tabletop exercise |
| `NFR-044` | Degraded mode | When Gold is unavailable, `RPT-012` and `RPT-021` are servable from the most recent frozen output with an explicit staleness banner. These two reports have deadlines that outrank freshness |
| `NFR-045` | Backup verification | Restores are tested monthly by actually restoring, not by confirming a backup exists |

## 7. Security

| ID | Requirement |
|---|---|
| `NFR-050` | Encryption at rest and in transit throughout, with keys managed outside the platform's own control plane |
| `NFR-051` | Entitlement resolution adds no more than 200 milliseconds at p95 to any query. A slow control gets disabled, so it must not be slow |
| `NFR-052` | Every data access is logged with principal, object, columns, row count and purpose where a purpose is required. Logs are retained 7 years and are themselves access-controlled |
| `NFR-053` | No standing privileged access to production data for platform engineers. Break-glass only, per [06, section 3.2](./06-governance-security-and-controls.md#32-what-this-means-for-the-platform) |
| `NFR-054` | Masking is applied in the query engine, not in the report layer. A direct query by any client must return the same masked result |
| `NFR-055` | Secrets never appear in code, configuration files, logs or error messages |
| `NFR-056` | Penetration testing annually, plus after any change to the entitlement model |

## 8. Observability

| ID | Requirement |
|---|---|
| `NFR-060` | Every pipeline emits run status, row counts, duration and quality results to a single telemetry store, queryable by D-01 and D-02 |
| `NFR-061` | SLO burn rate alerting on `NFR-004` fires at 50 % of the margin consumed, not at breach. An alert at breach is a notification, not a control |
| `NFR-062` | Every report displays its own freshness and quality, per `UR-01` and `UR-02`. Observability is a user-facing feature, not only an operational one |
| `NFR-063` | Cost is attributable to workload, to report and to consuming persona, so that expensive reporting is a visible business decision |
| `NFR-064` | A failed contract, a failed quality rule and a failed pipeline are three distinct alerts with three distinct responders |

## 9. Maintainability

| ID | Requirement |
|---|---|
| `NFR-070` | Metric definitions are code, versioned, reviewed and deployed through the same path as pipelines |
| `NFR-071` | Metadata in [05, section 5](./05-semantic-layer-and-metrics.md#5-metric-metadata-contract) is generated from deployed definitions, never hand-maintained |
| `NFR-072` | Schema evolution is additive by default. A breaking change follows the notice periods in [04, section 6](./04-data-contracts-and-slos.md#6-change-management-for-contracts) |
| `NFR-073` | A new report built from existing certified metrics and conformed dimensions is deliverable in under 10 working days. If it is not, the semantic layer is not doing its job |
| `NFR-074` | Every deployment is reversible within 30 minutes, including metric definition changes |

## 10. Environmental and cost

| ID | Requirement |
|---|---|
| `NFR-080` | Compute scales to zero outside its required windows. A warehouse running idle overnight is a defect |
| `NFR-081` | Total platform cost is reported monthly against a budget, attributed per `NFR-063` |
| `NFR-082` | Unused certified metrics and reports are identified quarterly from access logs and retired through change control. Retiring an unused report is a cost saving and a risk reduction |

---

## 11. Requirement conflicts and resolution

Some of these requirements pull against each other. Where they do, the resolution is stated here rather than being decided ad hoc in an incident.

| Conflict | Resolution |
|---|---|
| `NFR-004` availability against completeness | Availability wins. `RPT-012` publishes qualified at 09:00 rather than complete at 09:40, per `BR-DQ-012` |
| `NFR-011` ad-hoc concurrency against scheduled SLOs | Scheduled wins, enforced by the isolation in `NFR-015` |
| `NFR-051` entitlement latency against `CTL-011` thoroughness | Thoroughness wins. If enforcement cannot be made fast, the query is made cheaper, never the control weaker |
| `NFR-080` cost against `NFR-005` render latency | Latency wins during business hours; cost wins outside them |
| `NFR-024` storage tiering against `NFR-030` reproducibility | Reproducibility wins. Data required for reproduction stays on a tier that can serve it within `NFR-023` |
