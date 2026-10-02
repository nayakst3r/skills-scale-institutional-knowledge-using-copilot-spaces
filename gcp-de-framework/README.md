# GCP Data Engineering Framework — Team Operating Model

A reference repo layout and working method for **10 data engineers building one data
platform on Google Cloud with AI coding assistants**, without breaking what exists and
without drifting from the architecture. The standard toolset is **VS Code + GitHub Copilot**;
any other agent works too because the context lives in `AGENTS.md`.

**Presenting this?** Follow [`docs/DEMO_PLAYBOOK.md`](docs/DEMO_PLAYBOOK.md): repo setup, then 6
feature-build steps, each with a tested fallback (`make demo-step`).

## The core problem, and the core idea

| Problem | Why it happens with AI + 10 people | Answer in this repo |
|---|---|---|
| "We can't share context" | Each engineer's AI session starts cold. Architecture lives in people's heads and in chat. | **Context as code.** All context lives in the repo (`AGENTS.md`, `ARCHITECTURE.md`, ADRs, data contracts) and every AI tool is pointed at the same files. |
| Principles drift | Docs are advisory, and AI writes plausible code that ignores them. | **Principles as fitness functions.** Every principle that can be checked is checked in CI (`tools/check_principles.py`). Docs explain *why*; CI enforces *what*. |
| Features break existing pipelines | Shared BigQuery tables, implicit schemas, deploys from laptops. | **Contracts + ownership + gated deploys.** Every table has a contract, schema changes are checked for compatibility, CODEOWNERS own boundaries, only CI deploys. |
| Merge chaos | Long-lived branches, big AI-generated PRs. | **Trunk-based, small PRs, merge queue**, required checks, one PR = one concern. |

> Rule of thumb: **if a rule isn't in the repo, the AI doesn't know it; if it isn't in CI, people will eventually break it.**

## Reference architecture (Google stack)

```
Sources ──► Pub/Sub / Datastream / Storage Transfer
              │
              ▼
        GCS landing (raw, immutable)          ◄── Dataflow (streaming) where needed
              │
              ▼
  BigQuery  bronze ──► silver ──► gold        ◄── Dataform (SQLX) transforms + assertions
   (per-domain datasets: sales_bronze, sales_silver, sales_gold)
              │
              ▼
   Looker / Vertex AI / downstream consumers  ◄── only read gold via authorized views

Orchestration: Cloud Composer (Airflow)      Infra: Terraform     CI/CD: GitHub Actions + Cloud Build
Governance: Dataplex + Data Catalog tags     Secrets: Secret Manager    Auth: Workload Identity Federation
Environments: separate GCP projects  de-dev / de-stg / de-prod  (+ per-engineer sandbox datasets in dev)
```

## Repo layout

```
gcp-de-framework/
├── AGENTS.md                 # THE shared AI context. Every AI tool reads this first.
├── ARCHITECTURE.md           # Principles P1–P12, each with "how it's enforced"
├── CONTRIBUTING.md           # Branching, commits, PRs, merge, release
├── CODE_OF_CONDUCT.md        # Human + AI working agreement
├── docs/
│   ├── adr/                  # Architecture Decision Records (decisions + why)
│   └── TEAM_TOPOLOGY.md      # Who owns what among the 10 engineers
├── domains/<domain>/         # One folder per business domain (vertical slice)
│   ├── contracts/*.yaml      # Data contracts: schema, owner, SLA, compatibility
│   ├── transforms/*.sqlx     # Dataform transforms (bronze→silver→gold)
│   └── dags/*.py             # Composer DAGs (orchestration only, no business logic)
├── libs/de_common/           # Shared code — owned by platform team, versioned
├── platform/terraform/       # All infra. No console clicks.
├── tools/check_principles.py # Architecture fitness functions (run locally + CI)
├── .github/
│   ├── copilot-instructions.md   # Copilot entry point → AGENTS.md
│   ├── instructions/             # Copilot rules auto-applied by file type (SQLX, contracts, DAGs, Terraform)
│   ├── prompts/                  # Team slash commands: /new-table, /change-contract, /new-adr
│   ├── agents/                   # Custom agents: DE Planner, DE Architecture Reviewer
│   ├── workflows/                # ci, cd, copilot-setup-steps (Copilot coding agent)
│   ├── ISSUE_TEMPLATE/feature.yml  # Feature issues, assignable to a person or Copilot
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── .vscode/                  # Recommended extensions, Copilot settings, `make check` task
├── scripts/setup-github.sh   # Applies repo settings: squash-only, ruleset, labels, environments
├── demo/                     # Reference solutions for the demo playbook (delete after the show)
├── .pre-commit-config.yaml   # Same checks, run before every commit
└── Makefile                  # `make check` = what CI runs
```

> In a real repo, `.github/` must be at the repository root. It's nested here only so this
> template doesn't interfere with the exercise repo it lives in.

## How a feature flows (end to end)

1. **Issue** created from template → names the domain, the contract(s) touched, and whether it's a breaking change.
2. **Branch** from `main`: `feat/sales-123-daily-revenue` (lives ≤ 2 days).
3. **Build with AI**: the engineer's assistant loads `AGENTS.md` (Copilot, Gemini Code Assist, Claude Code all read it — see below). The engineer develops against their **sandbox dataset** in `de-dev` (`sbx_<username>_sales_silver`).
4. **Pre-commit** runs lint (sqlfluff, ruff), secrets scan, and `check_principles.py`.
5. **PR** (small, one concern) with the template filled in. CI runs:
   - fitness functions (architecture principles)
   - unit tests, `dataform compile`, BigQuery **dry-run** on `de-stg`
   - **contract compatibility** check vs. `main` (breaking change ⇒ blocked unless versioned)
   - Terraform `plan` posted as a PR comment
   - AI review (Copilot/Gemini code review) as an *advisory* reviewer
6. **Review**: CODEOWNERS auto-request the domain owner; a platform reviewer is added if `libs/`, `platform/`, or contracts change.
7. **Merge queue** re-runs checks against latest `main`, then squash-merges.
8. **CD**: merge to `main` auto-deploys to `de-stg` and runs Dataform assertions; a tagged release promotes to `de-prod` with manual approval (GitHub Environment protection).

## Making AI tools share one context

All assistants read from the same files, so every engineer's AI starts with the same architecture:

| Tool | File it reads | Set-up |
|---|---|---|
| GitHub Copilot (standard) | `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | Enabled by `.vscode/settings.json`. Prompt files and custom agents in `.github/prompts` and `.github/agents` are shared with everyone who opens the repo. Optionally add the repo + `docs/` to a team **Copilot Space** for chat on github.com. |
| Copilot coding agent | `AGENTS.md` + `copilot-setup-steps.yml` | Assign an issue to Copilot; its PR goes through the same checks and CODEOWNERS as anyone's. |
| Gemini Code Assist | `GEMINI.md` / code customization | Point at `AGENTS.md`; enable code customization on the repo. |
| Claude Code | `CLAUDE.md` | `@AGENTS.md` import. |
| Any other agent | `AGENTS.md` | Open standard, read natively by most agents. |

When a decision is made in a meeting or chat, it isn't done until it is an **ADR merged into
`docs/adr/`** and, if checkable, a **rule in `check_principles.py`**. That's how context
flows to 10 people's AI sessions without anyone having to "share" it.

## Copilot in the daily workflow

| Moment | What the engineer uses |
|---|---|
| Plan a feature | Chat → **DE Planner** agent → *Implement plan* handoff |
| Build | Agent mode + `/new-table` or `/change-contract`; auto-applied instructions per file type |
| Check | Task **check: architecture principles + tests** (Copilot runs it too); pre-commit on commit |
| Commit / PR | ✨ commit message (Conventional Commits); GitHub Pull Requests extension; Copilot code review |
| Review | Human CODEOWNERS + **DE Architecture Reviewer** agent for what CI can't check |
| Scale out | Well-scoped issues assigned to the Copilot coding agent |
| Learn | `/new-adr` → new rule in `AGENTS.md` + new check in `check_principles.py` |

## Try it

```bash
cd gcp-de-framework
make check                 # architecture checks + their tests + a full replay of the demo steps
make demo-step             # list the demo steps
```
