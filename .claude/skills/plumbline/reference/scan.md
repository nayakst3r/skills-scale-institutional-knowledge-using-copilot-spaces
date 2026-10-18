# /plumbline scan [path]

Read-only inventory of an existing repository. Changes nothing.

1. Run `plumbline scan --format json --root <path or .>` and parse it. Also keep the Markdown version
   (`plumbline scan`) for the user.
2. Present, in this order and briefly:
   - **Stack** — languages, frameworks, manifests, real commands found
   - **Modules** — the candidate modules table, including "could split into" suggestions for large ones
   - **Dependencies** — the observed import graph between modules; call out every **cycle** in plain words
     ("`core` imports `app` and `app` imports `core`, so neither can change without the other")
   - **Existing shared context** — which docs, ADRs, CODEOWNERS and CI already exist
   - **Gaps** — the scan's gap list, ordered by risk for parallel AI work (missing architecture/agents docs and
     cycles first)
   - **Existing guardrails** — hook manager, fitness functions, protection scripts, agent context; adoption must
     integrate with these
   - **CRITICAL** gaps (git-ignored source files, a nested `.github/` GitHub won't read) go first, in plain words
3. State the limits honestly: dependencies are traced for Python, JavaScript/TypeScript and dbt `ref()` only; other languages get
   folder-based modules without a dependency graph; module boundaries are a **proposal from folder structure**,
   not a design.
4. Offer the next step: `/plumbline adopt` to turn this into shared context for human review. Do not edit anything.
