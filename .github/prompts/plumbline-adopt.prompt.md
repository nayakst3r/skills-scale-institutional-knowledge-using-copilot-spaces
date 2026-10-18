---
name: plumbline-adopt
description: "Adopt Plumbline in this existing repository, alongside the guardrails it already has"
argument-hint: "[github|azure|gitlab]"
agent: agent
---
Run the Plumbline `adopt` command.

Read [the Plumbline skill](../../.claude/skills/plumbline/SKILL.md) and follow its `adopt` section and the reference file it points to,
exactly as written. The text the user typed after this prompt is the command's arguments.

Run Plumbline's engine with `python3 .claude/skills/plumbline/run.py …` where the skill says to. Respect `AGENTS.md` and `ARCHITECTURE.md`.
Never merge, approve or push to the default branch; stop and hand over with the review packet.
