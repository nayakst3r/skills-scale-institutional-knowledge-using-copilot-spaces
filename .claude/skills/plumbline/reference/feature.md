# /plumbline feature <issue-number>

Start an issue in parallel-safe isolation.

1. `gh issue view <n> --json number,title,body,labels` (or ask the user to paste it). Refuse to start without
   acceptance criteria and a named module — ask the user to complete the Feature issue template. If the issue isn't
   labelled `ready-for-agent`, ask the user to confirm a human has approved it (you may not add the label).
2. If the issue needs an architecture change, stop: `/plumbline adr` comes first.
3. Overlap check: `gh pr list --state open --json number,title,headRefName,files`. Name any open PR touching the
   same module.
4. Isolated workspace: `plumbline worktree new <n>` (creates `<repo>.worktrees/feat-<n>-<slug>` from the default
   branch). Work only there.
5. Load context: `ARCHITECTURE.md` (the module's `may_import`, `forbid_packages`), accepted ADRs, `AGENTS.md`,
   existing code in the module.
6. Show a short plan (files, tests). Every file inside the issue's module(s). Wait for approval.
7. Implement test-first where practical. `make test` and `plumbline check` must pass.
8. Commit (Conventional Commits + provenance trailers), push, `gh pr create --draft --fill`, completing the PR
   template (Closes #n, modules touched, architecture impact, AI disclosure, how verified).
9. Report worktree path, branch, PR link, test result, gate score. After merge: `plumbline worktree prune`.
