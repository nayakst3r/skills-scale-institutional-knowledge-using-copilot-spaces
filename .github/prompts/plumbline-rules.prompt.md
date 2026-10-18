---
name: plumbline-rules
description: "List, add, tune or disable coding rules"
argument-hint: "[list|add|tune|disable] [change]"
agent: agent
---
Run the Plumbline `rules` command.

Read [the Plumbline skill](../../.claude/skills/plumbline/SKILL.md) and follow its `rules` section and the reference file it points to,
exactly as written. The text the user typed after this prompt is the command's arguments.

Run Plumbline's engine with `python3 .claude/skills/plumbline/run.py …` where the skill says to. Respect `AGENTS.md` and `ARCHITECTURE.md`.
Never merge, approve or push to the default branch; stop and hand over with the review packet.
