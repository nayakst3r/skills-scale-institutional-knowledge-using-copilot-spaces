# /plumbline agents [change]

Edit `AGENTS.md` — the operating manual every AI agent in this repo loads (`CLAUDE.md` imports it; Codex, Copilot,
Cursor and others read `AGENTS.md` directly). Read `editing.md` first.

Typical changes: commands table (when build/test commands change), definition of done, branch naming, worktree
workflow, things agents must never do, stack-specific style rules.

Rules for this file:
- Instructions must be **checkable** — an agent must be able to tell whether it complied. Replace vague advice
  ("write clean code") with concrete rules ("functions over 50 lines need a reason in the PR").
- Keep it short. If a rule belongs to a specific module, put it in `ARCHITECTURE.md` section 7 instead.
- If a rule can be enforced mechanically, also propose a custom rule via `/plumbline rules add`, and say which.
- Commands in the table must actually work: run each one you add or change.
- Do not duplicate `AI_POLICY.md` content; link to it.
