# Project starter (Plumbline)

A greenfield repository template for teams where several engineers build features in parallel with AI agents.
Context lives in the repo, architecture is enforced on every edit and every PR, and `main` is protected.

## Start a new project — 6 steps
1. **Create your repo from this template** (GitHub → *Use this template*, or
   `gh repo create <org>/<name> --template <org>/<this-template> --private --clone`).
2. `make setup` — installs the git hooks.
3. **Edit `ARCHITECTURE.md`** — the only mandatory edit. Replace every `EDIT` marker and the `@your-org/` owners.
   In Claude Code: `/plumbline architecture`.
4. `make codeowners && make check-all` — must pass with score 100.
5. Add the `ANTHROPIC_API_KEY` repository secret (for the AI architecture review).
6. Open your first PR, then `make protect` (or `/plumbline protect`) to lock down `main`.

Then add your stack (`/plumbline new` patterns, or your own) and fill in the `test` target in the `Makefile`.

## What's here
| File | Purpose | Edit? |
|---|---|---|
| `ARCHITECTURE.md` | Modules, allowed dependencies, stack, conventions — machine-checked | **Yes, required** |
| `AGENTS.md` | Operating manual every AI agent loads | Rarely |
| `AI_POLICY.md` | Approved tools, data handling, disclosure, accountability | To match org policy |
| `CONTRIBUTING.md` | Parallel workflow: issues, worktrees, small PRs, commits | Rarely |
| `CODE_OF_CONDUCT.md`, `SECURITY.md` | Community and security process | Rarely |
| `docs/adr/` | Architecture decisions; required when `ARCHITECTURE.md` changes | Add new ADRs |
| `plumbline.toml` | Gate thresholds (policy as code) | Tune per project |
| `.github/` | Gate + AI review workflows, ruleset, templates, CODEOWNERS (generated) | Generated/rarely |

## Daily commands
`make test` · `make check` · `make check-all` · `make codeowners`

In Claude Code: `/plumbline feature <issue>` · `/plumbline check` · `/plumbline fix` · `/plumbline review` · `/plumbline adr`
