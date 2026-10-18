# /plumbline adr <title>

Record an architecture decision and apply it. Read `editing.md` first (branch `adr/<NNNN>-<slug>`).

1. Read `ARCHITECTURE.md` and all ADRs in `docs/adr/`. If an accepted ADR already covers this, say so and stop.
2. Next number = highest existing + 1, zero-padded to 4 digits. Copy `docs/adr/0000-template.md` to
   `docs/adr/<NNNN>-<slug>.md`.
3. Fill every section: status `Proposed`, today's date, deciders, context, decision, consequences — **including the
   exact change to the `plumbline-architecture` block** — and real alternatives with reasons. Ask for anything you
   cannot determine; never invent stakeholders or constraints.
4. Apply the change to `ARCHITECTURE.md` (prose and block). Mark any superseded ADR `Superseded by ADR-<NNNN>`.
5. `plumbline codeowners` if owners changed; `plumbline check --diff origin/main` must pass (PL014, PL015).
6. Commit `docs(adr): <NNNN> <title>`; PR requesting review from `architecture_owners`. No feature code in this PR.
