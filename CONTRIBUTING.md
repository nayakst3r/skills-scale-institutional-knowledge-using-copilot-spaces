# Contributing

Read `ARCHITECTURE.md`, `AGENTS.md` and `AI_POLICY.md` before your first change.

## Setup
```bash
git clone <repo-url> && cd <repo>
make setup        # installs git hooks (pre-commit gate + commit-msg provenance)
make test && make check
```

## Workflow for parallel work
1. **Start from an approved issue.** Bigger work goes `/plumbline grill` → `/plumbline spec` → `/plumbline tickets`;
   a human reviews the spec and tickets and labels the ones that are ready `ready-for-agent`. Small work uses the
   *Feature* template directly. It names the module, acceptance criteria and what is out
   of scope. One issue → one branch → one PR.
2. **Isolate your workspace** with a worktree, so parallel tasks never collide:
   ```bash
   python3 .claude/skills/plumbline/run.py worktree new 123     # → ../<repo>.worktrees/feat-123-<title>
   python3 .claude/skills/plumbline/run.py worktree list        # all worktrees with PR and review status
   python3 .claude/skills/plumbline/run.py worktree prune       # tidy up after merges (dry run first)
   ```
   With an agent: `/plumbline feature 123` does this and loads the right context.
3. **Stay in your module.** Cross-module refactors are their own PR, agreed with the owners first.
4. **Keep PRs small** (< ~400 changed lines) and short-lived (merge within 2 days). Rebase daily on `origin/plumbline-demo`.
5. **Open a draft PR early** so others can see what is in flight and avoid overlapping work.
6. **Architecture changes** go through an ADR PR first (`/plumbline adr`), reviewed by the architecture owners.

## Commits
Conventional Commits, plus a provenance trailer:
```
feat(orders): reject orders with zero quantity

AI-Assisted: yes
AI-Tool: claude-code
Human-Reviewed: Jane Citizen
```
Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `build`, `ci`.

## Pull requests
`plumbline-demo` is protected. Merging requires:
- **plumbline-gate** — deterministic checks: secrets, stubs, invented dependencies, architecture boundaries,
  shared-context files, ADR on architecture change
- **ai-architecture-review** — an AI reviewer checks the diff against `ARCHITECTURE.md`, ADRs and `AGENTS.md`
- **1 approving review from a human code owner** who is not the last person to push, with stale approvals
  dismissed on new pushes. AI review comments inform this decision; they never replace it. Nobody bypasses it.
- All review threads resolved, branch up to date, linear history (squash merge)

## Review etiquette
- Review the *behaviour*, not just the diff: check out the branch and run it for anything non-trivial.
- Ask "how did you verify this?" whenever the PR description doesn't say.
- A suppression (`plumbline: ignore PLxxx`) needs a reason the reviewer agrees with.

## Getting help
Open a discussion or ask in the team channel. Security issues: see `SECURITY.md`.
