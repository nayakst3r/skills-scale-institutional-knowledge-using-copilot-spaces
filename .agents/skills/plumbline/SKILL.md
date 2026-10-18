---
name: plumbline
description: "Keep AI-built software true to its architecture when many engineers and agents work in parallel, with a human approving every change. Scans existing repos and adopts them, or starts new ones; creates and edits shared context (ARCHITECTURE.md, AGENTS.md, AI_POLICY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, ADRs), coding rules, CI workflows and protected-branch settings; runs the quality gate. Use for \"/plumbline ...\", or when the user asks to set up, scan, adopt, edit or check architecture docs, AI policy, coding rules, CI quality gates, ADRs, human review or AI code-quality guardrails."
---

# /plumbline (Antigravity entry point)

Managed by Plumbline. The full skill and its engine are vendored once in `.claude/skills/plumbline/`, shared by
every agent this team uses (Antigravity, Claude Code, Copilot, Gemini CLI).

1. Read `.claude/skills/plumbline/SKILL.md` and follow it exactly, including the reference file it names for the command.
2. Run Plumbline's engine with `python3 .claude/skills/plumbline/run.py <command> …` (for example `python3 .claude/skills/plumbline/run.py check --staged`).
3. `AGENTS.md` and `ARCHITECTURE.md` are binding. Never merge, approve or push to the default branch; stop and
   hand over with the review packet.
