# /plumbline adopt [github|azure|gitlab] [--enforce]

Bring an **existing** repository under Plumbline, starting from what the code actually is. Everything lands on one
branch as a pull request for human review. Read `editing.md` and `human-review.md` first.

## 1. Prepare
- Working tree must be clean. `git fetch origin && git switch -c chore/adopt-plumbline origin/<default-branch>`.
- If `plumbline.toml` already exists, this is a re-run: use `/plumbline doctor` instead and fix what it reports.

## 2. Scan
- `plumbline scan --format json -o .plumbline/scan.json` and `plumbline scan -o .plumbline/scan.md`.
- Present the scan summary as in `scan.md`.

## 2b. Respect what's already there
The scan's **Existing guardrails** section lists the hook manager, fitness functions, branch-protection scripts and
agent-context files. Integrate with them:
- **CRITICAL gaps first.** Git-ignored source files and a nested `.github/` mean code or CI silently isn't there.
  Report them at the top of the hand-over; fixing them is the team's first decision.
- **Hooks:** if the repo uses the pre-commit framework, `init` adds Plumbline as a local hook — don't switch managers.
- **Fitness functions** (e.g. `tools/check_*.py`): reference them in `ARCHITECTURE.md`; don't re-implement their rules.
  Plumbline adds module boundaries (`may_import`, including dbt `ref()`) on top.
- **Branch protection:** if a script already sets it, `init` skips Plumbline's ruleset. In "Decisions for you", list
  what to add to that script: the `plumbline-gate` required check, ≥ 1 human code-owner approval, last-push
  approval, no bypass — and flag any mode that drops human approval (e.g. a `--solo` flag).
- **Runtime-provided packages** (Airflow on Composer/MWAA/Fabric, PySpark on Databricks): add them to
  `provided_packages` in `plumbline.toml` with a comment saying which runtime provides them.
- **Provenance trailer:** if `CONTRIBUTING.md` already defines one (e.g. `Assisted-by:`), set `ai_trailer_key` to it.

## 3. Ask the humans (one round, at most 4 questions, multiple choice where possible)
1. **Modules** — accept the proposed modules, or merge/rename/split (offer the "could split into" suggestions).
2. **Cycles** — for each cycle: which direction is intended? Or record it as known debt for now.
3. **Owners** — GitHub teams or people per module and for the architecture docs. If CODEOWNERS exists, propose
   what it already says.
4. **Strictness** — *warn mode* for the first sprint (recommended: findings reported, nothing blocked), or
   *enforce now*. `--enforce` on the command line means enforce now.
Anything not answered is written as `Unknown — decide by <owner>` and listed under "Decisions for you".

## 4. Scaffold without clobbering
`plumbline init --target . --ci <ci or auto> --baseline` — creates only what is missing, records existing findings as
baseline debt so only **new** problems fail, vendors the gate, guard and skill, and adds hooks.
Then in `plumbline.toml`: `fail_on = "never"` in warn mode; leave `"error"` when enforcing.

## 5. Write the shared context from reality
- **ARCHITECTURE.md** — if one existed, keep its prose and add the missing sections and the block; never delete the
  team's content. Otherwise replace the template with facts from the scan and the answers: purpose (from README),
  context, stack, real module table, and the `plumbline-architecture` block from the scan's proposal edited by the
  answers. Use `strict_placement = false` unless all code fits a module. Cycles accepted as debt stay allowed in
  `may_import` *and* are listed in the ADR below.
- **docs/adr/0002-baseline-architecture.md** — "Adopt the current architecture as the baseline": what was found,
  cycles and their intended direction, what will be tightened and when.
- **AGENTS.md** — use the scan's real commands (run the test command once and report the result; fix the table if it
  fails). Fold in rules from any existing `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md` or
  `AGENTS.md` — keep them, don't contradict them. Describe conventions you can see (test locations, naming, error
  handling style) and cite an example file for each.
- **CONTRIBUTING.md** — if it exists, keep it and add a short "Working with AI agents" section pointing to
  `AGENTS.md`, `AI_POLICY.md` and the human-review requirement. Otherwise use the template, adjusted to the real
  commands and branch names.
- **AI_POLICY.md** — ask whether an organisational AI policy exists; if so, link it at the top and keep only
  repo-specific rules. Otherwise keep the template and list it under "Decisions for you".
- **CODE_OF_CONDUCT.md / SECURITY.md** — template if missing; leave existing ones alone.
- **CODEOWNERS** — if none existed, generate with `plumbline codeowners`. If one existed, do **not** regenerate
  (the generated block would override it); show the human what owners the architecture implies instead.
- **CI** — add the Plumbline gate as a new workflow/pipeline; never edit existing ones in this PR. Add the AI
  pre-review only if the user wants it (it needs the `ANTHROPIC_API_KEY` secret).

## 6. Validate
- `plumbline check --all` — must pass (baseline hides existing debt; report how many baselined findings by rule).
- `plumbline doctor` — report remaining warnings (e.g. ruleset not yet applied).
- Remove `.plumbline/scan.json` from the commit; keep `scan.md` only if the user wants it in the repo.

## 7. Hand over
Commit `chore: adopt Plumbline (warn mode)` (or `(enforced)`), push, open a PR whose description includes the scan
summary, cycles, baselined debt counts and the next steps (`/plumbline protect` after merge; tighten
`strict_placement` and `fail_on` via later PRs). Then stop with the review packet. Do not merge, and do not run
`/plumbline protect` until the human has merged this PR.
