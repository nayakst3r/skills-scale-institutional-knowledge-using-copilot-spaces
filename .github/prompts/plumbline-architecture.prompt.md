---
name: plumbline-architecture
description: "Create, update, review or diagram ARCHITECTURE.md (the architecture contract)"
argument-hint: "[create|update|review|diagram] [notes]"
agent: agent
---
Run the Plumbline `architecture` command.

Read [the Plumbline skill](../../.claude/skills/plumbline/SKILL.md) and follow its `architecture` section and the reference file it points to,
exactly as written. The text the user typed after this prompt is the command's arguments.

Run Plumbline's engine with `python3 .claude/skills/plumbline/run.py …` where the skill says to. Respect `AGENTS.md` and `ARCHITECTURE.md`.
Never merge, approve or push to the default branch; stop and hand over with the review packet.
