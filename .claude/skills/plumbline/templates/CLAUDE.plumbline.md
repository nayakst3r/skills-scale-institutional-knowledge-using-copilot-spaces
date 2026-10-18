<!-- plumbline:begin (managed by /plumbline init — edit AGENTS.md and plumbline.toml, not this block) -->
## Shared project context (Plumbline)

@AGENTS.md

Before any code change, read `ARCHITECTURE.md` and the relevant ADRs in `docs/adr/`. They are binding.

A Plumbline hook checks every file you write — secrets, stubs, invented dependencies and architecture boundaries.
When it reports findings, fix them before moving on. Never suppress a rule just to get green.

Run `/plumbline check` before declaring a task done. For a new issue use `/plumbline feature <issue>`;
for an architecture change use `/plumbline adr`.
<!-- plumbline:end -->
