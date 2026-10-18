---
name: plumbline-tickets
description: "Slice an approved spec into single-module tickets in parallel waves"
argument-hint: "<spec-issue>"
agent: agent
---
Run the Plumbline `tickets` command.

Read [the Plumbline skill](../../.claude/skills/plumbline/SKILL.md) and follow its `tickets` section and the reference file it points to,
exactly as written. The text the user typed after this prompt is the command's arguments.

Run Plumbline's engine with `python3 .claude/skills/plumbline/run.py …` where the skill says to. Respect `AGENTS.md` and `ARCHITECTURE.md`.
Never merge, approve or push to the default branch; stop and hand over with the review packet.
