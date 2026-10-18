# /plumbline hooks [--write]

Git hooks generated from the repo's real stack, managed by **Lefthook** (github.com/evilmartians/lefthook).

1. `plumbline hooks --json` → show the detected sub-projects and tools (TypeScript `tsc`, ESLint, Prettier, Biome,
   Ruff, Black, `dotnet format`). Only tools declared in a manifest are used — never guessed.
2. `plumbline hooks` → show the proposed `lefthook.yml`:
   - **pre-commit** (parallel, skipped during merge/rebase): Plumbline gate on staged files; per sub-project
     formatters/linters on `{staged_files}` with `stage_fixed: true` (fixed files are re-staged); `tsc --noEmit` when
     TypeScript files are staged
   - **commit-msg:** AI provenance trailer check (`{1}` is the message file)
   - **pre-push:** Plumbline gate on the whole branch vs the default branch
3. If a hand-written `lefthook.yml` exists, don't overwrite it: show the Plumbline jobs to merge in, and edit it
   with the user's agreement.
4. Otherwise, with the user's go-ahead: `plumbline hooks --write --install`. If Lefthook isn't installed, offer the
   install that fits the repo (`npm install --save-dev lefthook` for Node projects — commit `package.json`;
   `pipx install lefthook`; `brew install lefthook`) and run `lefthook install` afterwards.
5. `plumbline doctor` should then show "Lefthook active" and "Hook jobs match the detected stack".
6. Personal overrides belong in `lefthook-local.yml` (git-ignored). Never add `skip`/`--no-verify` patterns that let
   commits bypass the gate.

## TypeScript repositories — programmatic hooks
In repos with TypeScript at the root (a `tsconfig.json` or a `typescript` dependency), `plumbline hooks --write`
also vendors typed hook scripts and creates the team's policy file (force with `--typescript`, skip with
`--no-typescript`):

| File | Owner | Purpose |
|---|---|---|
| `plumbline.hooks.mts` | **the team** — never overwritten | `defineHooks({...})`: protected branches, branch pattern, commit types, scope rules, trailer, forbidden files, size limit, and custom `checks.preCommit` / `checks.prePush` functions |
| `.plumbline/hooks/lib.mts` | Plumbline (refreshed) | Types (`HookPolicy`, `HookContext`, `Check`), git helpers, pure rule functions |
| `.plumbline/hooks/{pre-commit,commit-msg,pre-push}.mts` | Plumbline | Hook entry points |
| `.plumbline/hooks/run.mjs` | Plumbline | Launcher: Node's built-in type stripping (≥ 22.18 / 23.6), the flag (22.6+), or `npx tsx` |
| `.plumbline/hooks/lib.test.mts`, `tsconfig.json` | Plumbline | Unit tests (`node --test`) and strict type-checking |

What the TypeScript hooks enforce by default:
- **pre-commit:** no commits on protected branches; no secret/key files (`.env`, `*.pem`, `*.key`, …, with
  `.env.example` allowed); no oversized files; no merge-conflict markers; then the team's custom checks
- **commit-msg:** Conventional Commits; **scope must be a module from `ARCHITECTURE.md`** (plus repo-wide scopes like
  `deps`, `ci`, `docs`); header length; the `AI-Assisted` trailer when `requireAiTrailer` is on
- **pre-push:** no pushes or deletions on protected branches; feature branches must match the worktree naming
  (`feat/123-short-title`)

When the user wants a new rule ("block commits that touch `migrations/` without a rollback"), add a typed function
to `checks.preCommit` in `plumbline.hooks.mts` — it receives `ctx.stagedFiles`, `ctx.readStaged(path)`,
`ctx.branch` and `ctx.architectureModules` and returns a list of problems. Then:
1. `npx -p typescript -p @types/node tsc -p .plumbline/hooks` — must be clean
2. add a test case to `.plumbline/hooks/lib.test.mts` if the rule is a pure function, and run
   `node --test .plumbline/hooks/lib.test.mts`
3. prove it on a real staged change, then unstage

If the project's `tsconfig.json` would type-check the hook files, Plumbline adds `.plumbline` and
`plumbline.hooks.mts` to its `exclude` (or, if it has comments, tells the user to). Report that change.

Shared-hook changes go through `editing.md` (branch `chore/hooks`) and end with the review packet.
