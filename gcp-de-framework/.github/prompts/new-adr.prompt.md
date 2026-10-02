---
name: new-adr
description: Draft an Architecture Decision Record from a discussion or decision
argument-hint: <the decision in one sentence>
agent: agent
---
Draft the next ADR in `docs/adr/` using `0000-template.md` (number = highest existing + 1, status Proposed).
Fill Context, Decision, and Consequences from the chat message. Under Enforcement, propose the
concrete change to `tools/check_principles.py`, `CODEOWNERS`, or IAM that makes the decision stick, and
list the lines to add to `ARCHITECTURE.md` and `AGENTS.md`. Don't change other files.
