# /plumbline policy <ai | security | conduct | contributing> [change]

| Target | File |
|---|---|
| `ai` | `AI_POLICY.md` — approved tools, data handling, disclosure, IP, prohibited uses |
| `security` | `SECURITY.md` — reporting, secret exposure, built-in controls |
| `conduct` | `CODE_OF_CONDUCT.md` |
| `contributing` | `CONTRIBUTING.md` — setup, parallel workflow, commits, PR requirements |

Read `editing.md` first. With no change given, show the file's current key rules as a short summary and ask what
to change.

Policy-specific rules:
- **Never invent policy.** Approved tools, data classes, regulators, contacts and timeframes come from the user or
  their organisation's documents. If asked to "make it stricter" without specifics, propose options and ask.
- **AI policy ↔ enforcement.** When the AI policy changes something the tooling enforces, change the tooling in the
  same PR, or state clearly that it is not enforced:
  - provenance trailers → `require_ai_trailer` in `plumbline.toml`
  - data or secret rules → custom rules / PL001 patterns via `/plumbline rules`
  - review requirements → `.github/rulesets/main-protection.json` via `/plumbline protect`
- **Contributing ↔ reality.** Commands, check names and merge rules in `CONTRIBUTING.md` must match the Makefile,
  workflows and ruleset. Verify each.
- `CODE_OF_CONDUCT.md` adopts the Contributor Covenant by link. Do not paste its full text; add project-specific
  expectations only.
