# Security

## Reporting

Do not open a public issue for a security problem. Contact the repository owner
directly.

## Threat model

This repository holds a **model**, not customer data. No production data, no
credentials, no consent-bound CDR data belongs in it.

Live risks:

- **The ontology store MCP server is the only write path.** It stages; it never
  merges. Approval requires a human principal.
- **Token audience validation** (RFC 8707) is what stops a token minted for
  another MCP server working here. `agent/auth.py`, pinned to MCP authorization
  spec 2025-11-25.
- **Segregation of duties** is enforced at the token and again in the audit log.
  An agent approving its own proposal is a detectable breach, not a possibility.
- **The audit log is hash-chained.** Any edit or deletion breaks the chain and
  `verify()` reports the index.

## What must never be committed

- CDR consumer data, or any consent-bound data
- API keys, client secrets, mTLS certificates, CDR software statement assertions
- Real customer records in sample data
- Bank-published documents redistributed rather than cited
- `state/*.jsonl` — runtime audit and queue state

## Regulated context

If deployed inside an ADI, the ontology capability is in scope for APRA CPS 234
and, if it feeds a critical operation, CPS 230. Incident notification windows
are 72 hours for a material operational risk incident and 24 hours for
disruption to a critical operation beyond tolerance. See
`governance/tolerance-levels.md`.
