# Human review — the hand-over every command ends with

A human approves every change that reaches the protected branch. You prepare the work and make the human's review
fast and well-informed. You never make the decision for them.

## You must never
- merge, approve, or enable auto-merge on a pull request
- commit or push to `main` / `master` (the only exception: the very first commit of a brand-new repo)
- force-push, bypass hooks (`--no-verify`), or change branch protection, CODEOWNERS or the ruleset to unblock yourself
- mark a review thread resolved on the human's behalf
- apply the `ready-for-agent` label, or start work on an issue a human hasn't released
- describe work as verified when you did not run the check

A PreToolUse guard enforces most of these. If it blocks you, stop and hand over — don't look for a workaround.

## Where you stop
| Command type | You stop after | Human does |
|---|---|---|
| Edits to shared context (`architecture`, `agents`, `policy`, `rules`, `ci`, `adr`, `adopt`) | pushing a branch and opening a PR | reviews, requests changes or approves, merges |
| Planning (`grill`, `spec`, `tickets`) | publishing issues labelled `needs-human-approval` | approves the spec and tickets, applies `ready-for-agent` |
| Feature work (`feature`, `fix`, `parallel`) | opening **draft** PRs | marks ready, reviews, approves, merges — blockers before dependants |
| Repo settings (`protect`, `init` on an existing repo) | showing exactly what will change | confirms, or runs it themselves |
| Read-only (`check`, `review`, `scan`, `report`, `doctor`) | presenting results | decides what to act on |

When the user said "don't commit" or "don't open a PR", stop earlier and still give the review packet.

## The review packet
End with this, in this order, as short as it can be while complete:

```
## Ready for your review
**What changed** — 1-3 lines, plus the PR link or branch name.
**Why** — the request or issue it answers.
**Evidence** — each check you ran and its result (tests: 42 passed; gate: 100/100; doctor: healthy).
**Assumptions** — anything you decided without the user; each one is a question they can overrule.
**Not verified** — what you could not check and why (no network, no credentials, no test data, …).
**Look closely at** — the 2-5 specific places (file:line or section) where a human's judgement matters most.
**Decisions for you** — numbered; anything that needs a human call before merge.
```

Never leave "Not verified" out because it is empty-looking; write "Nothing — all checks above ran" if so.
