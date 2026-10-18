# Architecture

> **This is the one file every new project must edit.** It is the shared source of truth for every engineer and
> every AI agent working in parallel. CI fails while any `EDIT` marker remains.
> Changing this file after the first merge requires an ADR in `docs/adr/` (rule PL015).
> Run `/plumbline architecture` to fill it in interactively.

## 1. Purpose
<!-- EDIT: Two or three sentences. What does this system do, for whom, and what does success look like? -->

## 2. Context
<!-- EDIT: Upstream/downstream systems, users, external APIs, data sources. A list is fine. -->

## 3. Quality attributes (ranked)
<!-- EDIT: Rank the 3-5 that drive design trade-offs, e.g. 1. Security 2. Availability 99.9% 3. p95 latency < 300 ms -->

## 4. Constraints
<!-- EDIT: Cloud/region, data residency, compliance regimes, mandated platforms, budget. -->

## 5. Tech stack
<!-- EDIT: Language + version, frameworks, datastore, messaging, hosting, IaC. Agents must not add alternatives. -->

## 6. Modules and boundaries
Each module owns one responsibility. A module may depend only on the modules in its `may_import` list.
The block below is enforced by CI on every pull request and by the agent hook on every file an agent writes.

| Module | Responsibility | Owners |
|---|---|---|
| domain | Business entities and rules. Pure logic, no I/O. | core team |
| application | Use cases that orchestrate the domain through ports. | core team |
| adapters | HTTP API, persistence, messaging and third-party integrations. | platform team |
| shared | Small, stable cross-cutting utilities (logging, config, errors). | core team |

<!-- EDIT: Rename, add or remove modules to match your design, then update the block below to match the table. -->

```toml plumbline-architecture
source_roots = ["src"]
strict_placement = true          # new code must live inside a declared module
architecture_owners = ["@your-org/architects"]   # review shared context: this file, AGENTS.md, policies, CI

[[module]]
name = "domain"
paths = ["src/domain/**", "src/*/domain/**"]
may_import = ["shared"]
forbid_packages = ["requests", "httpx", "flask", "fastapi", "django", "sqlalchemy", "boto3",
                   "express", "axios", "pg", "mongoose", "prisma"]
owners = ["@your-org/core-team"]

[[module]]
name = "application"
paths = ["src/application/**", "src/*/application/**"]
may_import = ["domain", "shared"]
forbid_packages = ["flask", "fastapi", "django", "express"]
owners = ["@your-org/core-team"]

[[module]]
name = "adapters"
paths = ["src/adapters/**", "src/*/adapters/**"]
may_import = ["application", "domain", "shared"]
owners = ["@your-org/platform-team"]

[[module]]
name = "shared"
paths = ["src/shared/**", "src/*/shared/**"]
may_import = []
owners = ["@your-org/core-team"]
```

## 7. Cross-cutting conventions
- **Errors:** domain raises typed errors; adapters translate them to transport codes. Never swallow.
- **Configuration:** environment variables only, read once in `shared`, validated at start-up.
- **Logging:** structured JSON, correlation ID on every request, no personal data in logs.
- **Data access:** only through repository ports defined in `application`, implemented in `adapters`.
- **Testing:** domain and application are unit-tested without I/O; adapters get integration tests.

## 8. Key decisions
See [docs/adr](docs/adr/). The most recent accepted ADR wins over anything in this file it contradicts — and this
file should be updated in the same PR.
