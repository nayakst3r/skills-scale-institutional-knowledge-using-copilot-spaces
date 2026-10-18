# ADR-0001: Record architecture decisions and enforce them in CI

- **Status:** Accepted
- **Date:** project inception
- **Deciders:** Project tech lead

## Context
Several engineers work on this codebase in parallel, each assisted by AI coding agents. Agents have no memory
between sessions and will make locally plausible choices that drift from the intended design unless the design is
written down where they read it, and checked where they cannot ignore it.

## Decision
- `ARCHITECTURE.md` is the single source of truth for modules, allowed dependencies, stack and conventions.
  Its `plumbline-architecture` block is machine-checked on every agent edit, every commit and every pull request.
- Any change to `ARCHITECTURE.md` is accompanied by an ADR in this directory, in the same PR.
- `AGENTS.md` is the operating manual all AI agents load; `CLAUDE.md` imports it.
- `main` is protected: deterministic gate, AI architecture review and code-owner approval are required to merge.

## Consequences
- New engineers and agents get correct context from the repository alone.
- Architecture changes are slower and deliberate; feature work stays fast within the agreed boundaries.
- Module owners in `ARCHITECTURE.md` drive `CODEOWNERS`, so review routing follows the architecture.

## Alternatives considered
- Wiki-based architecture docs: not visible to agents, drift silently.
- Review-only enforcement: does not scale with parallel AI-generated changes.
