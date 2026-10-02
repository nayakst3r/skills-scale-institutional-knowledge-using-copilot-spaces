# Code of Conduct: humans and AI

## How we treat each other
- Be respectful and assume good intent. Critique code, not people.
- Review promptly. A blocked teammate costs more than an interrupted one.
- Disagree in the PR or ADR, not in side channels. Decisions that happen in chat get written down as an ADR, or they didn't happen.
- Anyone can say "stop, this breaks a principle", including the most junior engineer. That's expected, not rude.

## How we use AI
1. **You own what you commit.** If you can't explain a line, don't merge it.
2. **Give the AI the repo's context, not your private context.** Point it at `AGENTS.md`. If you find yourself repeatedly telling the AI something, add it to `AGENTS.md` in a PR so everyone's AI learns it.
3. **Don't let the AI bypass guardrails.** No disabling checks, `# noqa` or `--no-verify` to make it pass, or editing `check_principles.py` inside a feature PR.
4. **No sensitive data in prompts.** No production PII, customer data, or secrets pasted into any AI tool. Use sample or synthetic data.
5. **Approved tools only:** GitHub Copilot, Gemini Code Assist, and others on the approved list, using company accounts.
6. **Disclose assistance** with an `Assisted-by:` commit trailer. It helps reviewers calibrate.
7. **Keep AI PRs small.** Generating 2,000 lines is easy; reviewing them isn't. Split them.

## Ownership etiquette
- Changing another domain's code needs its owner's review (CODEOWNERS enforces this). Ask before you start, not at review time.
- Platform and `libs/` changes go in their own PR with a platform reviewer.
- Broke `main` or stg? Revert first, investigate second. No blame.

## Escalation
Raise conflicts with the domain lead, then the Architecture Guild. Conduct issues go to the engineering manager.
