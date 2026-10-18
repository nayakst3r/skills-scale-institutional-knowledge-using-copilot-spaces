# Domain docs layout

- **Single context.** One glossary for the whole repo: `GLOSSARY.md` at the root.
- **Decisions:** `docs/adr/NNNN-slug.md`. Write an ADR only when a decision is hard to reverse, would surprise a
  future reader without context, and came from a real trade-off between alternatives.
- **Architecture:** `ARCHITECTURE.md` is binding; its `plumbline-architecture` block is enforced by CI and hooks.
- **Reading order for agents:** `ARCHITECTURE.md` → `GLOSSARY.md` → relevant ADRs → the issue → the code in the
  issue's module.

Use glossary terms exactly in code, issues and specs. When a new term is needed, add it here via `/plumbline grill`.
