# Security Policy

## Reporting a vulnerability
Do not open a public issue. Use GitHub's **private vulnerability reporting** (Security tab → *Report a vulnerability*)
or contact the maintainers in `.github/CODEOWNERS` directly. Include the affected component, reproduction steps and
impact. Expect acknowledgement within 2 business days.

## Exposed secrets
If a secret was committed, pushed, or pasted into an AI tool:
1. Rotate or revoke it immediately — deleting it from the code does not make it safe.
2. Tell the maintainers so history and logs can be checked.
3. Record the incident per your organisation's process.

## Built-in controls
- Plumbline PL001 blocks common credential patterns at edit time, pre-commit and in CI.
- Enable GitHub secret scanning and push protection on this repository.
- Dependencies must be declared and pinned (PL006); enable Dependabot or your organisation's equivalent.
