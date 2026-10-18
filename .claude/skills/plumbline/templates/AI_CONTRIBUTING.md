# AI Contribution Standard

This repository accepts AI-assisted work. It does not accept unverified AI output.

**Unverified AI output** = output that looks finished but isn't: invented APIs or packages, stubs dressed as features,
tests that test nothing, comments that narrate, prose that fills space, and changes too large for anyone to
actually review.

## The rule
A human owns every line that merges. "The AI wrote it" is never an explanation for a defect.

## The controls (and where they run)

| Stage | Control | Mechanism |
|---|---|---|
| Prompt | Agent knows the rules | `CLAUDE.md` → *AI working rules* block |
| Generate | Agent self-checks each file it writes | Claude Code `PostToolUse` hook → `.plumbline/plumbline.py --hook` |
| Commit | Nothing obviously broken is committed | `.githooks/pre-commit` (`--staged`) + `commit-msg` provenance trailer |
| PR | Objective gate + score | CI job (`--diff`), SARIF to code scanning, sticky PR summary |
| Review | Human + AI review against the semantic rubric | PR template attestation, `/plumbline review` |
| Measure | Quality trends are visible | `/plumbline report` → `.plumbline/history.jsonl` |

## Commit provenance
When enabled in `plumbline.toml` (`require_ai_trailer = true`) every commit carries:
```
AI-Assisted: yes | partial | no
AI-Tool: claude-code
Human-Reviewed: Jane Citizen
```

## Suppressing a finding
False positives happen. Suppress on the line, with a reason a reviewer can judge:
```python
API_DOCS_EXAMPLE = "sk-example-not-real"  # plumbline: ignore PL001 — documentation fixture
```
Suppressions are visible in the diff and reviewed like code. Existing debt in brownfield repos is recorded once in
`.plumbline/baseline.json` and burned down over time — new code is held to the full standard from day one.

## Changing the policy
`plumbline.toml` is policy-as-code. Change it via PR with the tech lead as reviewer.
