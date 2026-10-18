# AGENTS.md — operating manual for AI coding agents

Every AI agent working in this repository (Claude Code, Copilot, Codex, Cursor or any other) follows this file.
Humans driving those agents are accountable for the result. Several engineers and agents work here **in parallel**;
the rules below exist so their work fits together without anyone re-explaining the system.

## 1. Load context before writing code
Read, in this order, every time you start a task:
1. `ARCHITECTURE.md` — modules, allowed dependencies, stack, conventions. **This is binding.**
2. `GLOSSARY.md` — the project's terms. Use them exactly.
3. `docs/adr/` — accepted decisions. A later ADR overrides an earlier one.
4. The issue you are working on — scope, acceptance criteria and *out of scope*. Only work on issues a human has
   labelled `ready-for-agent`.
5. The existing code in the module you will change. Match its patterns before inventing new ones.

If these conflict, stop and ask the human. Do not resolve architecture conflicts by guessing.

### Agent skills
Configuration for planning and ticketing skills lives in `docs/agents/`:
`issue-tracker.md` (where issues live), `triage-labels.md` (labels; only humans apply `ready-for-agent`) and
`domain.md` (glossary and ADR layout). Plumbline's `/plumbline grill`, `spec` and `tickets` use these files, as do
Matt Pocock's skills (`/grill-with-docs`, `/to-spec`, `/to-tickets`) if your team uses them.

## 2. One task, one module, one branch
- Work from an issue. Branch name: `feat/<issue>-<slug>`, `fix/<issue>-<slug>` or `chore/<slug>`.
- Use a separate git worktree per task so parallel sessions never share a working directory:
  `python3 .claude/skills/plumbline/run.py worktree new <issue>` (or `/plumbline feature <issue>`).
- Stay inside the module(s) the issue names. A change touching more than 3 modules fails CI (PL016).
- Rebase on `origin/plumbline-demo` before opening and before merging. `plumbline-demo` only accepts linear history.

## 3. Respect the architecture
- Only import from modules listed in your module's `may_import`. CI and the edit hook enforce this (PL013).
- Never add a package listed in your module's `forbid_packages`.
- New files go inside a declared module (PL017).
- If the task cannot be done within the current architecture: **stop**. Propose the change as an ADR
  (`/plumbline adr`) in its own PR. Do not edit `ARCHITECTURE.md` as a side effect of a feature.

## 4. Never invent
- Use only APIs, packages, flags and config keys you have verified exist — in this repo, its lockfile or official docs.
- New dependency = pinned manifest entry in the same PR, justified in the PR description.
- Do not create parallel versions of things that exist (a second HTTP client, logger, config loader or test helper).

## 5. Definition of done
A task is done only when all of these are true:
- [ ] Acceptance criteria in the issue are met — no stubs, placeholders or "rest of code" gaps
- [ ] Tests that would fail if the code were wrong are added and **pass locally** (`make test`)
- [ ] `make check` passes (Plumbline gate: score, boundaries, secrets, dependencies)
- [ ] Diff is under ~400 changed lines; otherwise split it
- [ ] PR description says what you verified and what you did not
- [ ] Commits carry the provenance trailer (see `CONTRIBUTING.md`)

## 6. Commands
| Purpose | Command |
|---|---|
| One-time setup after clone | `make setup` |
| Run tests | `make test` (Python) and `make build` (ingest sample NEM12, then dbt models + data tests on DuckDB) |
| Quality gate on your changes | `make check` |
| Whole-repo gate | `make check-all` |

## 7. Style
- Comments explain *why*; code explains *what*.
- Handle errors explicitly. No empty `catch` or `except: pass`.
- No secrets in code, config or tests. No debug output left behind.
- Write plainly in docs and PRs. No filler, no claims the code does not back up.

## 8. Human review — always
A human code owner reviews and approves every change before it reaches `plumbline-demo`. Your job ends when the PR is open
and you have handed over a review packet: what changed, why, evidence, assumptions, what you did **not** verify,
where to look closely, and decisions needed. A guard hook blocks merge/approve/push-to-main; do not work around it.

## 9. Things you must never do
- Merge, approve or enable auto-merge on a PR; resolve review threads on a human's behalf.
- Push or commit to `plumbline-demo`, force-push shared branches, or bypass hooks with `--no-verify`.
- Disable, weaken or suppress a Plumbline rule to get green. Suppressions need a written reason and human approval.
- Edit `AGENTS.md`, `AI_POLICY.md`, `ARCHITECTURE.md`, `plumbline.toml`, `.github/` or `CODEOWNERS` unless the issue
  is explicitly about them.
- Paste confidential, client or personal data into prompts beyond what `AI_POLICY.md` allows.
