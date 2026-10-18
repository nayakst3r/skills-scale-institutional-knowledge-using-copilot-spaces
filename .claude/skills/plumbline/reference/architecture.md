# /plumbline architecture [create | update | review | diagram] [notes or path]

`ARCHITECTURE.md` is the one file every project must edit. It holds the prose design and a
` ```toml plumbline-architecture ` block that the gate enforces on every agent edit, commit and PR.
Read `editing.md` first. Default mode: `create` if the file has unfinished markers, otherwise `update`.

## Block schema
```toml
source_roots = ["src"]                 # where application code lives
strict_placement = true                # code under source_roots must be inside a module (PL017)
architecture_owners = ["@org/team"]    # review all shared-context files
[[module]]
name = "domain"                        # unique
paths = ["src/*/domain/**"]            # globs, relative to repo root (dbt repos: ["domains/sales/**"])
may_import = ["shared"]                # modules this one may depend on — Python/JS/TS imports and dbt ref() (PL013); acyclic
forbid_packages = ["requests"]         # third-party packages this module must never import (PL013)
owners = ["@org/core"]                 # drives generated CODEOWNERS
```

## create
1. If a notes file or design doc path was given, read it. Inspect the repo: manifests, top-level folders,
   existing `src/` layout, CI, infrastructure code. Draft from reality, not from the template.
2. Ask only what you cannot infer, in one round of at most 4 questions: purpose and users · ranked quality
   attributes · hard constraints (cloud, region, compliance) · stack · module style (keep layered default /
   hexagonal / feature-sliced / custom) · GitHub team handles for owners.
3. Fill every section with specific facts; remove every unfinished marker. Unknowns become
   `Unknown — decide by <owner/date>`, never invented.
4. Make the module table and the block describe the same modules. Check `may_import` is acyclic and that every
   `paths` glob matches where this stack's code will live. Put I/O frameworks in inner modules' `forbid_packages`.
5. `plumbline codeowners`, then `plumbline check --all` until no PL014. Then continue at editing step 8.

## update
1. Has `ARCHITECTURE.md` been merged before (`git log --oneline -- ARCHITECTURE.md` on `origin/main`)? If yes,
   run the `adr` flow first; the ADR and this change go in the same PR.
2. Apply the change to prose and block together. For module changes, list which existing files would now
   violate the boundaries: run `plumbline check --all` and report any new PL013/PL017 as follow-up work.

## review
Read-only. Run `plumbline scan --format json` and compare its observed modules and import graph with the block in
`ARCHITECTURE.md`. Also compare the code against the prose: modules with no files, code outside modules, actual import
graph vs `may_import`, stack drift (packages in manifests not listed in section 5), stale sections contradicted by
ADRs. Report a table of drift items with a proposed fix for each. Do not edit.

## diagram
Read the block and draw the module dependency graph (boxes = modules with owners, arrows = `may_import`) as an
inline diagram. Offer to add a Mermaid version to `ARCHITECTURE.md` section 6 (via `update`).
