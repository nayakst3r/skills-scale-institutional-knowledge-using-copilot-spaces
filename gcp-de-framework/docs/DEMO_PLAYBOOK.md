# Demo playbook: repo setup and iterative feature build with VS Code + GitHub Copilot

**Audience:** engineering leads, data engineers, and client stakeholders.
**Message:** *With 10 engineers each using AI, consistency can't rely on people sharing context.
Put the context in the repo and the principles in CI. Then every Copilot session, human or agent,
builds within the same architecture, and nothing that exists gets broken.*

| | Full session | Short session |
|---|---|---|
| Length | ~75 min | ~30 min |
| Steps | 0 → 6 | 0 (pre-recorded), 1, 2, 4, 6 |

## Before the session (do this the day before)

- [ ] VS Code with the **GitHub Copilot** and **GitHub Pull Requests** extensions, signed in. Agent mode available in Chat.
- [ ] A GitHub account or org where you can create repos, with the **Copilot coding agent** enabled (needed for step 5).
- [ ] `gh` CLI logged in, Python 3.11+, `pip install pyyaml pytest ruff pre-commit`.
- [ ] Rehearse: `make check` must report **all tests passing**, and `tools/tests/test_demo_steps.py` replays every step below.
- [ ] Pre-create the demo repo (step 0) if you're doing the short session.
- [ ] Each step has a **fallback**: `make demo-step STEP=<name>` applies the reference solution if live Copilot output goes off track. Use it without apology. The point is the process, not the generation.

Copilot's output isn't deterministic. The guardrails are. When Copilot gets something wrong
live, that's the best moment of the demo: show CI catching it.

---

## Step 0: Repo setup (10 min). "The repo is the shared brain"

**Do**

```bash
gh repo create <org>/gcp-de-platform --private --clone
cp -R gcp-de-framework/. gcp-de-platform/ && cd gcp-de-platform
git add -A && git commit -m "chore: bootstrap data platform repo" && git push -u origin main
./scripts/setup-github.sh <org>/gcp-de-platform --solo     # omit --solo for a real team
pre-commit install --hook-type pre-commit --hook-type commit-msg
code .
```

**Show, in this order**
1. `AGENTS.md`: "This is what every engineer's Copilot reads first. Ten people, one context."
2. `ARCHITECTURE.md`: the *Enforced by* column. "A principle without enforcement is a wish."
3. `.github/instructions/*.instructions.md`: rules that load automatically by file type (SQLX, contracts, DAGs, Terraform).
4. `.github/prompts/` and `.github/agents/`: the team's reusable `/new-table` and `/change-contract` commands, and the *DE Planner* and *DE Architecture Reviewer* agents.
5. GitHub → **Settings → Rules**: the `main-protection` ruleset (PR required, checks required, no force-push), plus `CODEOWNERS`.

**Prove it's loaded.** In Copilot Chat (Ask mode):
> What do I need to do to add a new BigQuery table in this repo?

Copilot answers with contracts, `ref()`, assertions, and gold-only cross-domain reads, and lists
`AGENTS.md` and the instructions under *References*. Nobody briefed it; the repo did.

**Talking point:** the 4 layers. Shared context (AGENTS.md), automated checks (`check_principles.py`),
ownership (CODEOWNERS), and gated delivery (rulesets and environments).

---

## Step 1: First feature by a new team (15 min). "Plan, then build within the rules"

**Story:** the Finance pod joins. They need daily revenue in EUR. Sales already exists and must not break.

**Do**
1. Create a branch from the status bar: `feat/finance-1-revenue-eur`.
2. Chat → agent picker → **DE Planner**:
   > Finance needs a gold table with daily revenue converted to EUR, per channel. FX rates land in finance_bronze.raw_fx_rates.
3. Point out that the plan reads Sales through `sales_gold.revenue_daily` (P3), proposes contracts, and slices the work into PRs.
4. Click the **Implement plan** handoff, or run the prompt file:
   > /new-table domain=finance layer=gold table=revenue_eur_daily purpose=daily revenue in EUR per channel, using sales_gold.revenue_daily and a new finance_silver.fx_rates
5. Copilot creates the contracts, transforms, and DAG, then runs **check: architecture principles + tests** itself and fixes any violations.
6. Source Control: ✨ to generate the commit message (a Conventional Commit, as AGENTS.md requires). Commit, and pre-commit runs.
7. GitHub Pull Requests view → **Create Pull Request**. The template asks for *Contracts touched* and *Breaking change?*.
8. On the PR, add **Copilot** as a reviewer. CI runs `principles`, `lint`, and `secrets`. CODEOWNERS requests `@org/de-finance` and `@org/de-platform` (contracts changed).

**Fallback:** `make demo-step STEP=iteration-1-finance-domain`

**Talking point:** a team that has never seen the Sales code built on it correctly, because the
context came from the repo and not from a meeting.

---

## Step 2: The guardrail moment (5 min). "AI goes off-architecture and CI says no"

**Do**: in agent mode, without the prompt file, give the naive request:
> Make the EUR revenue table count orders by joining the orders table with fx rates.

The most detailed table is `sales_silver.orders`, so assistants often reach for it. If Copilot does,
the `make check` task fails. If Copilot instead refuses and cites P3, that's the instructions
working; show it, then apply the "what a careless edit looks like" version:

```bash
make demo-step STEP=iteration-2-guardrail-broken
make check
#  domains/finance/transforms/gold_revenue_eur_daily.sqlx: [cross-domain-read] reads sales_silver; only other domains' gold is allowed
```

Push it to the PR to show the red **principles** check blocking the merge. Then revert:
`make demo-step STEP=iteration-1-finance-domain`.

**Talking point:** the reviewer didn't need to spot it. Sales can now refactor `sales_silver`
freely without breaking Finance.

---

## Step 3: Additive change to a live table (8 min). "Evolve without breaking"

**Do**
> /change-contract table=sales/orders change=add a nullable region column

Copilot classifies the change as **additive**, adds the column to the contract and transform, and bumps
`1.1.0 → 1.2.0`. Run **check: contract compatibility vs main**: it passes.

**Fallback:** `make demo-step STEP=iteration-3-additive-column`

**Talking point:** the contract is the API between teams. Additive changes flow freely.

---

## Step 4: Breaking change (10 min). "The repo won't let you break consumers"

**Do (a), the wrong way, to show the block:**
> Rename amount to gross_amount in sales orders.

Or apply `make demo-step STEP=iteration-4a-breaking-broken`, then run the compatibility task:

```
domains/sales/contracts/orders.yaml: [contract-compat] breaking change: column 'amount' removed. Create orders_v2.yaml instead (P5)
```

**Do (b), the right way:**
> /change-contract table=sales/orders change=rename amount to gross_amount

Copilot classifies it as **breaking**, leaves `orders` untouched, creates `orders_v2` (`2.0.0`), marks v1
`deprecated` with a sunset date, and lists consumers (`sales_gold.revenue_daily`) that must migrate.

**Fallback:** `make demo-step STEP=iteration-4b-breaking-as-v2`

**Talking point:** consumers migrate on their own schedule. Nothing breaks at merge time.

---

## Step 5: Delegate to the Copilot coding agent (12 min). "Agents follow the same process as people"

**Do**
1. GitHub → **Issues → New → Data feature**:
   - Domain: sales
   - Outcome: add `avg_order_value` to `sales_gold.revenue_daily` for the Looker dashboard
   - Breaking: No
2. **Assign to Copilot.** The coding agent starts in an environment set up by
   `.github/workflows/copilot-setup-steps.yml` (it runs `make check` first), reads `AGENTS.md`, and opens a draft PR.
3. While it works (a few minutes), go through `copilot-setup-steps.yml` and the issue form.
4. On the agent's PR: the same CI checks, CODEOWNERS, and PR template apply. No special path for AI.
5. Locally, check out the PR and run the **DE Architecture Reviewer** agent on it. Leave a review comment such as
   `@copilot also add avg_order_value to the contract description` to show iteration through review.

**Fallback** (if the agent is slow): `make demo-step STEP=iteration-5-coding-agent` on a branch, then open the PR yourself.

**Talking point:** scale comes from agents doing well-scoped issues. The rulesets and checks are what make that safe.

---

## Step 6: The team learns (8 min). "Turn a review comment into a guardrail"

**Story:** in a retro, a reviewer says, "Twice this sprint someone wrote an incremental table without a
`uniqueKey`, and a re-run duplicated rows." Today P7 is only on the review checklist.

**Do**
> /new-adr Incremental Dataform tables must declare a uniqueKey so re-runs and backfills are idempotent.

Then apply the enforcement (or have Copilot write it from the ADR's *Enforcement* section):

```bash
make demo-step STEP=iteration-6-new-guardrail
git diff --stat      # check_principles.py, its test, ARCHITECTURE.md, AGENTS.md
make check
```

**Talking point:** this is how context spreads without meetings. One PR updates the docs
(ARCHITECTURE.md), every engineer's Copilot (AGENTS.md), and CI (`check_principles.py`). The next time
anyone's AI writes an incremental table, it already knows, and if it forgets, CI catches it.

---

## Close (2 min): what to take away

| Challenge | Mechanism shown |
|---|---|
| Can't share context across 10 people and their AIs | `AGENTS.md` + instructions + prompt files + custom agents, all versioned in the repo (step 0) |
| Architecture principles drift | Automated architecture checks in pre-commit and CI (steps 2 and 6) |
| New features break what exists | Data contracts + compatibility check + `_vN` versioning (steps 3 and 4) |
| Uncontrolled merges | Ruleset: PR + required checks + CODEOWNERS + squash; merge queue for real teams (steps 0 and 1) |
| AI agents at scale | Coding agent works issues within the same gates as people (step 5) |
| Rules stay current | Retro → ADR → check, owned by a rotating context curator (step 6) |

## After the session

Delete `demo/`, `scripts/demo-step.sh`, and `tools/tests/test_demo_steps.py` (the test skips itself
once `demo/` is gone), drop `--solo` by re-running `setup-github.sh` without it, and connect GCP
(the repo variables listed at the end of `setup-github.sh`).
