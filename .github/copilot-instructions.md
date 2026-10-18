# Copilot instructions

<!-- plumbline:begin (managed by /plumbline init — edit AGENTS.md and plumbline.toml, not this block) -->
## Shared project context (Plumbline)

Read `AGENTS.md` first and follow it. Before any code change, read `ARCHITECTURE.md` and the relevant ADRs in
`docs/adr/`; they are binding. Only work on issues a human has labelled `ready-for-agent`.

Run the quality gate before declaring a task done: `python3 .claude/skills/plumbline/run.py check --diff origin/HEAD` (or `/plumbline-check`).
Fix findings rather than suppressing them. Never merge, approve or push to the default branch: a human code owner
approves every pull request. End every task with the review packet described in `AGENTS.md`.
<!-- plumbline:end -->
