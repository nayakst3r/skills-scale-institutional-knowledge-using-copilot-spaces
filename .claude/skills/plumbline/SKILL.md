---
name: plumbline
description: Keep AI-built software true to its architecture when many engineers and agents work in parallel, with a human approving every change. Scans existing repos and adopts them, or starts new ones; creates and edits shared context (ARCHITECTURE.md, AGENTS.md, AI_POLICY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, ADRs), coding rules, CI workflows and protected-branch settings; runs the quality gate. Use for "/plumbline ...", or when the user asks to set up, scan, adopt, edit or check architecture docs, AI policy, coding rules, CI quality gates, ADRs, human review or AI code-quality guardrails.
argument-hint: "<command> [args] — scan | adopt | init | new | grill | spec | tickets | parallel | worktree | hooks | architecture | agents | policy | rules | ci | adr | feature | check | fix | review | protect | report | doctor"
---

# /plumbline

Keep AI-built software true to its architecture. By Deloitte Australia AI & Data Engineering.
Shared context, architecture-as-code, mandatory human review and quality gates for teams building in parallel
with AI agents.

## How to run a command
1. Parse the first word of the arguments as the command. With no command, show the table below and ask what the
   user wants to do. In a repo that already has code but no `plumbline.toml`, suggest `scan` then `adopt` rather
   than `init`. If the request is in plain English ("add Copilot to our AI policy"), map it to the command.
2. **Read `reference/<command>.md` from this skill's folder and follow it exactly.** Do not work from memory.
   For any command that creates or edits a shared-context file, also read `reference/editing.md` first.
   Every command that changes files also follows `reference/human-review.md`.
3. The CLI is stdlib Python 3.11+. Run it as `plumbline <subcommand>` if that is on PATH
   (`command -v plumbline`), otherwise `python3 <this-skill-folder>/run.py <subcommand>`.
   In a repo that has been initialised, `python3 .plumbline/plumbline.py` is the pinned gate.

## Commands

| Command | Purpose |
|---|---|
| **Set up** | |
| `init [github\|azure\|gitlab] [--strict] [--baseline]` | Scaffold shared context, gates, hooks, CI and this skill into the current repo |
| `scan [path]` | Read-only inventory of an existing repo: stack, modules, real import graph, cycles, gaps |
| `adopt [github\|azure\|gitlab] [--enforce]` | Bring an existing repo under Plumbline from what the code actually is (warn mode first) |
| `new <name> <python\|node\|dotnet>` | Create a greenfield project with everything wired in from commit one |
| `doctor` | Check the setup is complete and consistent, and fix what is not |
| **Create & edit shared context** | |
| `architecture [create\|update\|review\|diagram] [notes]` | Write or change `ARCHITECTURE.md` (prose + machine-checked module block) |
| `agents [change]` | Edit `AGENTS.md`, the operating manual every AI agent loads |
| `policy <ai\|security\|conduct\|contributing> [change]` | Edit `AI_POLICY.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` or `CONTRIBUTING.md` |
| `rules [list\|add\|tune\|disable] [change]` | Edit coding rules and gate thresholds in `plumbline.toml` (incl. custom regex rules) |
| `ci [add\|update\|explain] [job]` | Add or change CI jobs (GitHub Actions, Azure DevOps, GitLab) keeping required checks in sync |
| `adr <title>` | Record an architecture decision and apply it to `ARCHITECTURE.md` |
| `hooks [--write]` | Generate Lefthook git hooks from the detected stack (gate, TS/ESLint/Prettier/Ruff/…, trailers) |
| **Plan → build in parallel** | |
| `grill [topic]` | One-question-at-a-time interview that sharpens a plan against the architecture; updates glossary and ADRs |
| `spec [title]` | Turn the conversation into a spec issue for human approval (modules, seams, architecture impact) |
| `tickets <spec>` | Slice an approved spec into one-module tickets with blockers and parallel waves |
| `parallel <spec\|tickets…>` | Build the next wave of human-approved tickets in separate worktrees, each to a draft PR |
| `worktree [new\|list\|remove\|prune]` | One isolated worktree per issue, with PR and review status |
| **Daily work** | |
| `feature <issue>` | Start an issue in its own worktree and branch, scoped to its module, with a draft PR |
| `check [staged\|all\|<branch>]` | Run the gate and explain findings |
| `fix [scope]` | Fix findings and re-run until green |
| `review [branch\|PR#]` | Semantic review against the architecture and a 10-point rubric |
| `protect [owner/repo]` | Apply protected-main rules (required checks, code owners, linear history) |
| `report [--since 30d]` | Score trend, rule hotspots and AI-provenance mix |

## Human review is mandatory
Every command that changes anything ends at a human: read `reference/human-review.md` and finish with its review
packet. You never merge, approve, push to `main`, bypass hooks or weaken protections — a human code owner approves
every change. A guard hook blocks those commands; if it fires, stop and hand over.

## Always
- Shared-context files are owned by the architecture owners. Edit them on a branch and open a PR for human review.
- Never invent facts about the user's system, organisation or policies. Ask, or write `Unknown — decide by <owner>`.
- Never weaken a rule, threshold or protection to get a check green unless the user explicitly asks; then record why.
