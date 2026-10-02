# AI-Assisted Engineering at Scale: Data & AI Practice

**Context as code. Principles as CI.**
A best-practice operating model, with a working sample framework, for keeping intent and architecture
intact when a large practice builds data platforms with AI coding assistants.

| | |
|---|---|
| **Owner** | Office of the Chief AI Officer, Data & AI practice |
| **Audience** | Every engineer, tech lead, and architect in the practice |
| **Status** | Internal reference. The framework is a *sample*: adapt it per engagement (see [Adapting it](#adapting-it-for-a-client)) |
| **Standard tools** | VS Code + GitHub Copilot (other approved assistants work through `AGENTS.md`) |
| **Stacks** | Microsoft Fabric / Azure, Databricks, Snowflake, Google Cloud, AWS |

> **Assumptions in this README.** It describes how the practice is *expected* to use this
> material. Items in `[brackets]` are placeholders for firm-specific links and contacts (AI policy,
> brand library, support channel). Firm policy, client contracts, and Risk & Quality guidance always
> take precedence over anything written here.

---

## Contents

1. [Why this exists](#why-this-exists)
2. [What's in this repository](#whats-in-this-repository)
3. [The model in one page](#the-model-in-one-page)
4. [How the practice uses it](#how-the-practice-uses-it)
5. [Starting an engagement: the first engineer's checklist](#starting-an-engagement-the-first-engineers-checklist)
6. [Day to day: how every engineer works](#day-to-day-how-every-engineer-works)
7. [Using AI responsibly on engagements](#using-ai-responsibly-on-engagements)
8. [Adapting it for a client](#adapting-it-for-a-client)
9. [Rolling it out across the practice](#rolling-it-out-across-the-practice)
10. [Measuring whether it works](#measuring-whether-it-works)
11. [Contributing back](#contributing-back)
12. [Status and known limits](#status-and-known-limits)
13. [Support](#support)

---

## Why this exists

AI assistants make every engineer faster. Across a large practice, they also multiply **drift**:
code that compiles and passes review but quietly breaks the design. Examples:
- a model reading another team's internal tables
- a column renamed in place, breaking every downstream consumer
- a production path hard-coded "just for now"
- a model shipped without tests

Two things don't scale against that:

- **Documents.** Architecture decks and wikis are advisory; an AI session never reads them.
- **Reviewers.** Nobody can hold every rule in their head across hundreds of pull requests a week.

What does scale is putting the intent where every engineer and every AI will meet it: **in the
repository** (as context every assistant reads) and **in CI** (as checks every change must pass).

> Rule of thumb: **if a rule isn't in the repo, the AI doesn't know it. If it isn't in CI, someone will eventually break it.**

## What's in this repository

| Path | What it is | Who it's for |
|---|---|---|
| [`data-platform-framework/`](data-platform-framework/) | The sample framework: a ready-to-copy repo with rules, checks, Copilot setup, CI/CD, and five stack options | Tech leads starting an engagement |
| [`data-platform-framework/docs/DEMO_PLAYBOOK.md`](data-platform-framework/docs/DEMO_PLAYBOOK.md) | A scripted live demo (30 or 80 min): repo setup, then six feature-build steps, each with a tested fallback | Anyone presenting the model |
| [`data-platform-framework/stacks/README.md`](data-platform-framework/stacks/README.md) | Concept map: how each idea maps to Fabric/Azure, Databricks, Snowflake, GCP, AWS | Architects, presales |
| [`brag-output-2026-10-02-121404/`](brag-output-2026-10-02-121404/) | **The practice walkthrough video** (81 s, Deloitte-branded), poster, share copy, and sources to re-edit it | Leadership comms, onboarding |
| [`brag-output/`](brag-output/) | An earlier 22-second cut (superseded) | — |

The framework's own [README](data-platform-framework/README.md) is the technical guide. It is
deliberately client-neutral because it is copied into client repositories.

## The model in one page

| Layer | What it means | Where it lives in the framework |
|---|---|---|
| **1. Context as code** | One shared set of instructions every AI assistant reads first, versioned with the code | `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/`, `.github/agents/` |
| **2. Principles as CI** | Every architecture principle that can be checked is a check that blocks the pull request | `ARCHITECTURE.md` ("Enforced by" column) + `tools/check_principles.py` |
| **3. Ownership** | Teams own their domain; shared contracts and platform code need a second owner | `.github/CODEOWNERS`, data contracts in `domains/*/contracts/` |
| **4. Gated delivery** | Only CI deploys; `main` is protected; production needs a human approval | Rulesets (`scripts/setup-github.sh`), `cd.yml`, GitHub Environments |
| **5. Learning loop** | A repeated review comment becomes a rule and a check in one PR | ADRs in `docs/adr/`, `/new-adr` prompt, rotating "context curator" |

The video shows all five layers in 81 seconds.

## How the practice uses it

### Roles

| Role | Responsibility |
|---|---|
| **Office of the Chief AI Officer** | Owns this standard and the AI usage guidance; approves changes to the core principles |
| **Framework maintainers** (practice platform guild) | Maintain `data-platform-framework`, the stack overlays, and the checks; publish versioned releases |
| **Engagement tech lead** (*"the first engineer"*) | Sets up the client repo from the framework, adapts the rules, owns `AGENTS.md` and the ruleset for the engagement |
| **Engagement Architecture Guild** (1 per pod + tech lead) | Reviews ADRs and PRs labelled `needs-architecture`; keeps `ARCHITECTURE.md` honest |
| **Engineers** | Build features with AI inside the rules; run `make check` before every PR; raise rules that should exist |
| **Release captain** (rotating) | Approves production promotions |
| **Context curator** (rotating, monthly) | Turns repeated review comments and AI mistakes into `AGENTS.md` rules and new checks |

### Engagement lifecycle (assumed)

```
Pursuit / mobilise ──► Kick-off ──► Step 1: repo setup ──► Steps 2–5: delivery ──► Handover
  choose the stack       agree where     first engineer          every change through      client team owns the
  (stacks/README.md)     the repo lives  (checklist below)       the same gates            repo, rules and CI
```

**Where the repository lives** depends on the engagement contract. Typically it is the **client's
GitHub organization**, so the client owns the code, CI, and history from day one. A firm-hosted repo
is used only when the contract says so. Confirm this with the engagement leadership and Risk &
Quality before kick-off.

## Starting an engagement: the first engineer's checklist

Target: a protected repo, with a green baseline and the team's rules in place, on day one.

**1. Create the repo and choose the stack**
```bash
gh repo create <client-org>/<engagement>-data-platform --private --clone
cp -R data-platform-framework/. <engagement>-data-platform/ && cd <engagement>-data-platform
./scripts/use-stack.sh                    # lists: aws, azure-fabric, databricks, gcp, snowflake
./scripts/use-stack.sh <stack>
pip install -r requirements.txt -r requirements-stack.txt
make check && make local-build            # must be green before anyone else joins
```

**2. Make the context the client's own**
- [ ] Rename the sample domains in `domains/` (and in `CODEOWNERS`) to the client's real domains.
- [ ] Review `AGENTS.md`: add client naming standards, regulatory constraints, and approved services.
- [ ] Review `ARCHITECTURE.md`. Every principle the client cares about either has an "Enforced by", or a ticket to add one.
- [ ] Record the stack choice and any deviations as ADRs in `docs/adr/`.

**3. Protect `main`**
```bash
./scripts/setup-github.sh <client-org>/<engagement>-data-platform --merge-queue
```
- [ ] Create the GitHub teams named in `CODEOWNERS`.
- [ ] Add the release captain as required reviewer on the `prod` environment.
- [ ] Turn on secret scanning with push protection, Copilot code review, and the Copilot coding agent (if the client's licence allows).

**4. Connect the cloud** (follow `stacks/<stack>/README.md`)
- [ ] OIDC trust between GitHub and the client cloud. **No long-lived keys in GitHub.**
- [ ] Repo and environment variables set; `stack-validate` and `cd` stop skipping cloud steps.

**5. Onboard the team**
- [ ] Run the 30-minute version of the demo playbook with the team, on the client's stack.
- [ ] Every engineer installs the recommended VS Code extensions and pre-commit hooks.
- [ ] First PR per engineer is paired.

## Day to day: how every engineer works

| Moment | What you do |
|---|---|
| Pick up work | Issue from the *Data feature* form: domain, contracts touched, breaking or not |
| Plan | Copilot Chat → **DE Planner** agent → *Implement plan* |
| Build | Copilot agent mode with `/new-table` or `/change-contract`; the right instructions load automatically per file type |
| Check | `make check` and `make local-build` (Copilot runs them too). Fix failures; never bypass them |
| Commit | Conventional Commit message; add `Assisted-by: <tool>` when AI helped |
| PR | Small (one concern, < ~400 lines), template filled in; five required checks; CODEOWNERS review |
| Merge | Through the merge queue (squash) |
| Spot a gap | Propose a rule: `/new-adr`, then a PR that updates `AGENTS.md` and adds a check |

Breaking a data contract is never done in place: create `<table>_v2` with a deprecation date. The
`/change-contract` prompt walks you through it.

## Using AI responsibly on engagements

These complement, and never replace, the firm's AI policy `[link: firm AI policy]` and the
engagement's contractual terms.

1. **Use approved tools only**, with firm- or client-provided accounts, as the engagement allows.
2. **You own every line you commit.** If you can't explain it, don't merge it.
3. **No client confidential data, personal data, or secrets in prompts**, unless the client agreement and the tool's data handling explicitly allow it. Use the sample data pattern (`sample_data/`) for local work.
4. **Don't let AI bypass guardrails**: no disabling checks, `--no-verify`, or weakening `check_principles.py` inside a feature PR.
5. **Disclose assistance** with an `Assisted-by:` trailer, so reviewers can calibrate.
6. **AI-authored PRs follow the same path as human ones**: same checks, same owners, same approvals. There is no fast lane.
7. **Client IP stays with the client.** Improvements flow back to the framework only after sanitisation (see [Contributing back](#contributing-back)).

## Adapting it for a client

| You can change | Keep (the core of the model) |
|---|---|
| The stack (`use-stack.sh`) and native tools via an ADR (Dataform, Lakeflow pipelines, dynamic tables, …) | Shared AI context in the repo (`AGENTS.md` + Copilot instructions) |
| Domain names, layers, naming conventions | Principles enforced in CI as required checks |
| Additional principles and checks (add them, with tests) | Data contracts with backward-compatibility checks |
| Orchestrator, cloud services, environments | Protected `main`, CODEOWNERS, squash + merge queue |
| PR size limits, review counts, release cadence | Only CI deploys; human approval for production; OIDC, no stored keys |

If a client constraint forces you to drop something in the right-hand column, record it as an ADR
and tell the framework maintainers. That is a signal the standard needs to evolve.

## Rolling it out across the practice

Suggested approach for a practice of several hundred engineers:

| Wave | Who | What |
|---|---|---|
| **0. Show** | Whole practice | All-hands: the [walkthrough video](brag-output-2026-10-02-121404/brag.mp4) + a live 30-minute demo |
| **1. Champions** | 1 tech lead per account / offering | Run the full 80-minute playbook hands-on; each sets up one real engagement |
| **2. New engagements** | All new data engagements | Start from the framework by default; exceptions need an ADR |
| **3. Existing engagements** | Teams with active repos | Adopt incrementally: `AGENTS.md` first, then the ruleset, then the checks one at a time |
| **4. Steady state** | Everyone | Quarterly framework release; context curators share new rules across engagements |

Enablement assets: the walkthrough video, [`DEMO_PLAYBOOK.md`](data-platform-framework/docs/DEMO_PLAYBOOK.md), and
the concept map in [`stacks/README.md`](data-platform-framework/stacks/README.md).

## Measuring whether it works

Suggested signals, all available from GitHub and CI without extra tooling:

| Signal | What good looks like |
|---|---|
| PRs blocked by `principles` (and then fixed) | Non-zero early on (the gates are catching drift), trending down as `AGENTS.md` improves |
| Breaking-contract incidents reaching staging or production | Zero |
| Median PR size and time to merge | Small PRs, merged within a day |
| Share of PRs that are AI-assisted (`Assisted-by:`) | Rising, with no rise in incidents |
| New rules added through the learning loop | A steady trickle: the practice is learning |
| Time from kick-off to protected, green repo | Day one |

## Contributing back

The framework improves when engagements feed lessons back. Do this **without client data or IP**.

1. Generalise the change (no client names, schemas, data, or business logic).
2. Open a PR against `data-platform-framework` with tests (`make check`), and run `scripts/verify-all-stacks.sh` if you touched shared code.
3. Changes to core principles need approval from the Office of the Chief AI Officer. New stack overlays and checks need the framework maintainers.
4. Maintainers publish versioned releases (`vYYYY.MM`) with release notes, so engagements can upgrade deliberately.

## Status and known limits

**Verified:**
- The architecture checks and their tests (26 passing), including a replay of every demo step on all five stacks.
- A real local build of every model on DuckDB.
- An offline `dbt parse` with each stack's adapter.
- `terraform validate` against each stack's provider.
- All workflow files lint clean with actionlint.

**Not yet verified:**
- Deploy pipelines against a live cloud account.
- The Airflow and Databricks job files in a running orchestrator.
- The Copilot instruction, prompt, and agent files in a live Copilot session.

Rehearse on the target stack before relying on these.

The **Deloitte wordmark in the video is recreated in type**. Replace it with the official logo from the brand library `[link: brand library]` before any use outside the practice.

## Support

- Questions and proposals: `[practice channel]`
- Framework maintainers: `[team / distribution list]`
- AI policy questions: `[Office of the Chief AI Officer contact]`

---

*This branch replaces the original GitHub Skills exercise README. When the framework moves to its own
repository, this file becomes that repository's README.*
