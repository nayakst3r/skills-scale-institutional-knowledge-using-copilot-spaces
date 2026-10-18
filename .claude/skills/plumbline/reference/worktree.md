# /plumbline worktree [new <issue> | list | remove <issue> | prune]

Thin wrapper over `plumbline worktree`; run the CLI and present its output.

| Command | What it does |
|---|---|
| `plumbline worktree new <issue> [--slug s] [--type feat\|fix\|chore\|refactor\|docs\|spike\|adr] [--copy-env]` | Fetches, creates `<repo>.worktrees/<type>-<issue>-<slug>` on branch `<type>/<issue>-<slug>` from `origin/<default>`. Slug comes from the GitHub issue title via `gh` when available. Refuses closed issues and existing branches. |
| `plumbline worktree list [--json]` | Every worktree with its branch, PR state, review decision, and whether it has uncommitted or unpushed work. |
| `plumbline worktree remove <issue\|branch>` | Removes one worktree, keeps the branch. Refuses if there are uncommitted changes. |
| `plumbline worktree prune [--yes]` | Dry run by default. Marks for removal only worktrees whose PR is merged/closed or whose branch is merged after having commits. Never removes a fresh worktree with no commits yet. |

Git hooks (Lefthook or `.githooks`) apply in every worktree automatically. `.env` files are not copied unless
`--copy-env` is passed — say so when relevant. Ask before running `prune --yes` or `remove`.
