# Data Platform Framework — Team Operating Model

A reference repo and working method for **a team of ~10 data engineers building one data platform
with AI coding assistants**, without breaking what exists and without drifting from the
architecture. It works the same on **Microsoft Fabric / Azure, Databricks, Snowflake, Google Cloud,
and AWS**. The standard toolset is **VS Code + GitHub Copilot**; any other agent works too, because
the context lives in `AGENTS.md`.

**Presenting this?** Follow [`docs/DEMO_PLAYBOOK.md`](docs/DEMO_PLAYBOOK.md): set up the repo on a
stack of your choice, then 6 feature-build steps, each with a tested fallback (`make demo-step`).

## The core problem, and the core idea

| Problem | Why it happens with AI + 10 people | Answer in this repo |
|---|---|---|
| "We can't share context" | Each engineer's AI session starts cold. Architecture lives in people's heads and in chat. | **Context as code.** All context lives in the repo (`AGENTS.md`, `ARCHITECTURE.md`, ADRs, data contracts, Copilot instructions) and every AI tool reads the same files. |
| Principles drift | Docs are advisory, and AI writes plausible code that ignores them. | **Principles as fitness functions.** Every principle that can be checked is checked in CI (`tools/check_principles.py`). Docs explain *why*; CI enforces *what*. |
| Features break existing pipelines | Shared tables, implicit schemas, deploys from laptops. | **Contracts + ownership + gated deploys.** Every table has a versioned contract, breaking changes are blocked, CODEOWNERS own boundaries, and only CI deploys. |
| Merge chaos | Long-lived branches, big AI-generated PRs. | **Trunk-based, small PRs, merge queue**, required checks, one PR = one concern. |
| Different clients, different stacks | Each stack has its own tools and habits. | **One method, five stacks.** The method, contracts, checks, and dbt models are stack-neutral; a stack is a swappable overlay (`scripts/use-stack.sh`). |

> Rule of thumb: **if a rule isn't in the repo, the AI doesn't know it; if it isn't in CI, people will eventually break it.**

## Reference architecture (any stack)

```
Sources ──► landing (object storage / streaming)                       [stack-specific ingestion]
              │
              ▼
   <domain>_bronze ──► <domain>_silver ──► <domain>_gold                [dbt: portable SQL + data tests]
     raw, immutable      cleaned, conformed    public interface: the only layer other domains read
              │
              ▼
   BI / ML / other domains (read gold only)

Per domain:   contracts/ (the API)   models/ (dbt)   orchestration/ (schedule only)
Platform:     Terraform (schemas, grants)   CI/CD (GitHub Actions + OIDC)   environments: local · dev sandbox · ci · stg · prod
```

| | Fabric / Azure | Databricks | Snowflake | Google Cloud | AWS |
|---|---|---|---|---|---|
| Warehouse | Fabric Warehouse | Unity Catalog (Delta) | Snowflake | BigQuery | S3 + Iceberg + Athena |
| Orchestration | Fabric Airflow job | Lakeflow Jobs | Airflow | Cloud Composer | MWAA |
| CI login | Entra OIDC | Databricks WIF | Key-pair secret | GCP WIF | AWS OIDC |

Full concept map: [`stacks/README.md`](stacks/README.md).

## Repo layout

```
data-platform-framework/
├── AGENTS.md                 # THE shared AI context (+ a stack section written by use-stack.sh)
├── ARCHITECTURE.md           # Principles P1–P12, each with "how it's enforced"
├── CONTRIBUTING.md           # Branching, commits, PRs, merge, release
├── CODE_OF_CONDUCT.md        # Human + AI working agreement
├── dbt_project.yml           # One dbt project for every domain, portable across stacks
├── profiles.yml              # Connection targets (local DuckDB in the template; cloud targets per stack)
├── macros/                   # Naming convention, physical_layout(), portable tests, CI cleanup, grants
├── domains/<domain>/
│   ├── contracts/*.yaml      # Data contracts: logical schema, owner, SLA, PII, version
│   ├── models/               # dbt models <domain>_<layer>_<table>.sql + tests/sources YAML
│   └── orchestration/        # Schedules dbt only (Airflow DAG or Databricks job, per stack)
├── sample_data/              # Small CSVs so everything builds locally on DuckDB
├── stacks/<stack>/           # The 5 stack overlays + concept map (stacks/README.md)
├── platform/terraform/       # Infra for the selected stack (from its overlay)
├── libs/de_common/           # Shared Python (config; how Airflow runs dbt)
├── tools/check_principles.py # Architecture fitness functions (pre-commit + CI)
├── docs/                     # ADRs, team topology, demo playbook
├── demo/                     # Reference solutions for the demo playbook (delete after the show)
├── scripts/                  # use-stack, setup-github, demo-step, verify-all-stacks
├── .github/
│   ├── copilot-instructions.md   # Copilot entry point → AGENTS.md
│   ├── instructions/             # Copilot rules auto-applied by file type (dbt models, contracts, orchestration, Terraform)
│   ├── prompts/                  # Team slash commands: /new-table, /change-contract, /new-adr
│   ├── agents/                   # Custom agents: DE Planner, DE Architecture Reviewer
│   ├── workflows/                # ci (stack-neutral), stack-validate + cd (per stack), copilot-setup-steps
│   ├── ISSUE_TEMPLATE/feature.yml  # Feature issues, assignable to a person or Copilot
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── .vscode/                  # Recommended extensions, Copilot settings, check/build tasks
└── Makefile                  # make check · make local-build · make use-stack · make demo-step
```

> In a real repo, `.github/` must be at the repository root. Copy this folder's contents to the
> root of a new repo (playbook step 0).

## How a feature flows (end to end)

1. **Issue** from the *Data feature* form: domain, contracts touched, breaking or not.
2. **Branch** from `main`: `feat/sales-123-daily-revenue` (lives ≤ 2 days).
3. **Build with Copilot**: it loads `AGENTS.md` and the instructions for the file type. Build locally
   (`make local-build`, DuckDB) and in your cloud sandbox (`DBT_TARGET=dev`, schemas `sbx_<you>_*`).
4. **Pre-commit** runs lint, secret scan, and `check_principles.py`.
5. **PR** (small, one concern), with the template filled in. Required checks:
   - `principles`: architecture checks + contract compatibility against `main`
   - `local-build`: every model built and tested on DuckDB with sample data
   - `stack-validate`: offline `dbt parse` with the stack's adapter + `terraform validate`; once connected, `dbt build --empty` in the real warehouse
   - `lint`, `secrets`
6. **Review**: CODEOWNERS request the domain owner, plus platform for contracts, `macros/`, `platform/`. Copilot review is advisory.
7. **Merge queue** re-runs checks against the latest `main`, then squash-merges.
8. **CD**: merge → stg (Terraform, `dbt build`, publish orchestration); release tag → prod after approval.

## Copilot in the daily workflow

| Moment | What the engineer uses |
|---|---|
| Plan a feature | Chat → **DE Planner** agent → *Implement plan* handoff |
| Build | Agent mode + `/new-table` or `/change-contract`; instructions auto-applied per file type |
| Check | Tasks **check** and **local-build** (Copilot runs them too); pre-commit on commit |
| Commit / PR | ✨ commit message (Conventional Commits); GitHub Pull Requests extension; Copilot code review |
| Review | Human CODEOWNERS + **DE Architecture Reviewer** agent for what CI can't check |
| Scale out | Well-scoped issues assigned to the Copilot coding agent |
| Learn | `/new-adr` → new rule in `AGENTS.md` + new check in `check_principles.py` |

Other assistants read the same context: Claude Code (`CLAUDE.md` → `AGENTS.md`), Gemini Code Assist
(`GEMINI.md`), and any agent that reads `AGENTS.md`.

## Try it

```bash
pip install -r requirements.txt
make check                     # architecture checks + tests (incl. replaying the demo on all 5 stacks)
make local-build               # build + test every model on DuckDB
./scripts/use-stack.sh         # list stacks;  ./scripts/use-stack.sh snowflake  to choose one
make demo-step                 # list the demo steps
```
