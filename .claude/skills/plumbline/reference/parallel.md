# /plumbline parallel <spec-issue | ticket numbers…> [--max 3]

Run approved tickets **in parallel**, each in its own git worktree, each ending as a draft PR for human review.

1. Collect candidate tickets: the spec's sub-issues (`gh api repos/{owner}/{repo}/issues/<spec>/sub_issues`) or the
   numbers given. Keep only open tickets labelled **`ready-for-agent`** (applied by a human). List any skipped and
   why.
2. **Choose the wave:** tickets whose blockers are all closed/merged, that touch **different modules**, and whose
   module has no other open PR (`gh pr list --state open --json headRefName,files`). Cap at `--max` (default 3).
   Show the wave and wait for the user's go-ahead.
3. For each ticket: `plumbline worktree new <ticket>` (prints the path). Then run the `feature.md` flow **inside
   that worktree**, from step 5 (load context) onwards. If your agent can start independent sub-agents, give each
   ticket to its own sub-agent with: the worktree path, the ticket, `feature.md`, `human-review.md`, and the rule
   "work only inside this worktree". Otherwise do them one after another.
4. Each ticket ends with a **draft** PR and a review packet. Never merge, approve, or start a ticket whose blocker
   is merely *open as a PR* — blockers must be merged by a human first.
5. Hand over one combined table:
   ```
   | Ticket | Module | Worktree | Draft PR | Tests | Gate | Needs human attention |
   ```
   followed by each ticket's "Not verified" and "Decisions for you", and the next wave that will unblock once these
   are merged. Suggest `plumbline worktree prune` after merges.
