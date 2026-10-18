---
name: plumbline-feature
description: "Start work on an approved issue in its own worktree and branch"
argument-hint: "<issue>"
agent: agent
---
Run the Plumbline `feature` command.

Read [the Plumbline skill](../../.claude/skills/plumbline/SKILL.md) and follow its `feature` section and the reference file it points to,
exactly as written. The text the user typed after this prompt is the command's arguments.

Run Plumbline's engine with `python3 .claude/skills/plumbline/run.py …` where the skill says to. Respect `AGENTS.md` and `ARCHITECTURE.md`.
Never merge, approve or push to the default branch; stop and hand over with the review packet.
