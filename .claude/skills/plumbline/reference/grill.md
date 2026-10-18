# /plumbline grill [topic]

A relentless, one-question-at-a-time interview that sharpens a plan **and checks it against the architecture**,
updating the glossary and decision records as decisions land. Inspired by Matt Pocock's `/grill-with-docs`
(github.com/mattpocock/skills); this version also tests every decision against `ARCHITECTURE.md`.

The human is the decider. You ask; they answer. Never answer your own questions or move on without their answer.

## Before the first question
Read `ARCHITECTURE.md` (modules, `may_import`, `forbid_packages`), `GLOSSARY.md` (or the glossary named in
`docs/agents/domain.md`), accepted ADRs, and the code in the modules the topic touches. If no topic was given, ask
for it in one line.

## The loop
Ask **one question at a time**, each with your recommended answer and one line of why, so the human can reply
"yes" quickly. Work down the decision tree: resolve a branch fully before opening the next. After each answer:

1. **Terms** — if the answer uses a fuzzy or conflicting word ("account" vs "customer"), challenge it and agree
   one term. Add or update it in `GLOSSARY.md` (term · meaning · not to be confused with). Glossary only — no
   implementation detail.
2. **Architecture** — name the module that will own the behaviour. If it would need a new dependency between
   modules, a package the module forbids, or a new module, say so plainly: that is an architecture change.
3. **Reality** — check claims against the code ("the order service already retries" → find it or say it isn't
   there). Use concrete scenarios to test edge cases.
4. **Decision records** — offer an ADR only when the decision is hard to reverse, would surprise a future reader,
   and came from a real trade-off. Write it with the `adr` flow (status `Proposed`) — architecture changes always
   get one.

Keep a running **decision log** in the conversation (numbered, one line each).

## Stop when
Every branch is resolved, or the human says stop. Then:
- show the decision log, the glossary changes and any ADRs drafted
- list **open questions** that still need someone (name who, if known)
- say whether it's ready for `/plumbline spec`

Glossary and ADR edits follow `editing.md` (branch `docs/<topic>`), and end with the review packet from
`human-review.md`. If nothing was written, no branch is needed.
