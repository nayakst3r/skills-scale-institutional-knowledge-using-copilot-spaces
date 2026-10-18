# Issue tracker

- **Tracker:** GitHub Issues, used through the `gh` CLI (`gh issue create`, `gh issue view`, `gh issue edit`).
- **Specs** are issues titled `Spec: <name>` with the `spec` label.
- **Tickets** are issues created from a spec, linked to it as **sub-issues**, each with a `module:<name>` label that
  matches a module in `ARCHITECTURE.md`, and a "Blocked by" section listing other tickets.
- **Pull requests are not requests for work.** Work starts from an issue.

This file follows the `docs/agents/` layout used by Matt Pocock's agent skills, so those skills and Plumbline read the
same configuration.
