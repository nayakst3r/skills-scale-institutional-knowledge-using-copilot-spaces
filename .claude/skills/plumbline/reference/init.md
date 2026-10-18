# /plumbline init

Scaffold Plumbline into the current repository. Arguments: CI platform (`github` | `azure` | `gitlab` | `none`,
default auto-detect), `--strict` (require AI provenance trailers), `--baseline` (brownfield), `--no-governance`,
`--no-skill`, `--clients` (coding agents to set up `/plumbline` for: `all` by default, or a comma list of `claude`,
`copilot`, `gemini`, `antigravity`; ask which agents the team uses if it isn't obvious).

0. If the repo already has application code and history, stop and recommend `/plumbline adopt` instead — it builds
   the architecture from the code rather than from a template. Continue with `init` only if the user insists.
1. Confirm the repo root: `git rev-parse --show-toplevel`. If not a git repo, ask whether to `git init -b main`.
2. Brownfield (existing code and history)? Add `--baseline` unless the user said otherwise, so existing debt is
   recorded and only new problems fail. Also plan to set `strict_placement = false` until code is reorganised.
3. Preview: `plumbline init --target . --ci <ci> [flags] --dry-run`. Show the planned files as a short table:
   created / skipped (already exists). Ask to proceed.
4. Run without `--dry-run`. Existing files are never overwritten unless the user asks (`--force`).
5. Mention what each agent now has: Copilot `/plumbline-<command>` prompt files and the cloud-agent setup steps,
   Gemini CLI `/plumbline` and `/plumbline:<command>` (each person trusts the project hooks once), Antigravity
   `/plumbline`. They all read the same `.claude/skills/plumbline/SKILL.md`. Later: `plumbline clients`.
6. Run `plumbline doctor`. Unfinished `ARCHITECTURE.md` sections are expected at this point.
7. Tell the user the next steps, only those that apply:
   1. `/plumbline architecture` — the one required edit
   2. GitHub: add the `ANTHROPIC_API_KEY` repo secret (AI architecture review)
   3. Commit the scaffold on a branch: `chore: adopt Plumbline`, open a PR
   4. After both checks have run once: `/plumbline protect`
   - Azure DevOps: register `pipelines/plumbline.azure-pipelines.yml` and add it as a Build Validation policy.
   - GitLab: `include: { local: pipelines/plumbline.gitlab-ci.yml }` in `.gitlab-ci.yml`.
