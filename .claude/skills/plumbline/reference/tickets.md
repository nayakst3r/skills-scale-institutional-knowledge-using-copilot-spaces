# /plumbline tickets <spec-issue>

Break an approved spec into tickets that **several engineers and agents can build in parallel without
colliding**. Inspired by Matt Pocock's `/to-tickets`; this version slices along architecture modules and computes
which tickets can run at the same time.

1. Read the spec issue (`gh issue view <n> --json title,body,labels`). If it still has `needs-human-approval` and
   the user hasn't said it's approved, ask before continuing.
2. Read `ARCHITECTURE.md` and the code in the modules involved.
3. **Slice.** Each ticket is a thin vertical slice that can be demonstrated or tested on its own and fits one agent
   session. Rules:
   - **One module per ticket** where possible. If a slice spans modules, split it along the `may_import` direction
     (the depended-on module first). Never more than 3 modules.
   - **Prefactoring first:** refactors that make the feature easy are their own tickets, earlier in the order.
   - **Wide mechanical changes** use expand → migrate callers in batches → contract, one ticket each.
   - Each ticket names its **blockers**. Tickets without blockers can start immediately.
4. **Parallel plan.** Group tickets into waves: a wave contains tickets whose blockers are all in earlier waves and
   which touch **different modules** (two agents in one module collide). Show it:
   ```
   Wave 1: #a (domain)  #b (adapters)        ← can run in parallel worktrees
   Wave 2: #c (application, blocked by a)
   ```
5. Present titles, modules, blockers, acceptance criteria and waves. Iterate with the human until they approve the
   breakdown. Do not publish before that.
6. **Publish blockers-first.** For each ticket: body in the Feature-template shape (Outcome · Module(s) ·
   Acceptance criteria · Out of scope · Blocked by #… · Spec #…), then
   `gh issue create --title "<title>" --label module:<name> --label needs-human-approval --body-file <file>`.
   Link it under the spec as a sub-issue:
   `gh api repos/{owner}/{repo}/issues/<spec>/sub_issues -X POST -F sub_issue_id=$(gh api repos/{owner}/{repo}/issues/<ticket> --jq .id)`
   (if the API is unavailable, the "Spec #…" line is the link). Never edit or close the spec issue. Never add
   `ready-for-agent`.
7. Hand over: ticket list with waves, and "Label the tickets you approve `ready-for-agent`; then
   `/plumbline parallel <spec>` or `/plumbline feature <ticket>`."
