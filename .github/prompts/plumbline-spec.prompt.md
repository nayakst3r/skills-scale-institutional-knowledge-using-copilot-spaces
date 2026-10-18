---
name: plumbline-spec
description: "Write a spec (problem, stories, acceptance, out of scope) for human approval"
argument-hint: "[title]"
agent: agent
---
Run the Plumbline `spec` command.

Read [the Plumbline skill](../../.claude/skills/plumbline/SKILL.md) and follow its `spec` section and the reference file it points to,
exactly as written. The text the user typed after this prompt is the command's arguments.

Run Plumbline's engine with `python3 .claude/skills/plumbline/run.py …` where the skill says to. Respect `AGENTS.md` and `ARCHITECTURE.md`.
Never merge, approve or push to the default branch; stop and hand over with the review packet.
