# CPS 230 tolerance levels — ontology capability

Only meaningful if the ontology feeds a critical operation. Confirm that first.

| Dimension | Tolerance | Measured by | Breach action |
|---|---|---|---|
| Ontology store availability | 99.5% monthly | MCP server health checks | Notify within 24h if a critical operation is disrupted beyond tolerance |
| Gate integrity | 100% — no merge without an open gate | CI record | Halt pipeline, kill-switch agent writes |
| Audit chain validity | 100% | `AuditLog.verify()` daily | Treat as a security incident under CPS 234 |
| Segregation of duties | zero breaches | `segregation_breaches()` daily | Revoke agent write credentials |
| Unverified share of assertions | below 40% | `unverified_report` | Stewardship escalation, not an incident |
| Source freshness (tier 1) | under 48 hours | watcher timestamps | Investigate; stale source is a data quality issue |
| Drift rate | under 5% of sampled assertions | monthly re-verification | Steward review of affected domain |

Notification obligations, verbatim from CPS 230: material operational risk
incidents within **72 hours**; disruption to a critical operation outside
tolerance within **24 hours**.
