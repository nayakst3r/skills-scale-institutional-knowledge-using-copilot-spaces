# ADR-0002: Domain modules and medallion layers

- **Status:** Accepted
- **Date:** 2026-10-18
- **Deciders:** @nayakst3r (architecture owner)

## Context
Several engineers, each working with an AI agent, will build ingestion, metering, customer and billing in parallel.
Without agreed boundaries, billing logic drifts into metering models, DAGs grow SQL, and one domain starts reading
another's half-cleaned tables.

## Decision
- Six modules (ARCHITECTURE.md §6): `ingestion`, `shared`, `orchestration` (Python) and `metering`, `customer`,
  `billing` (dbt). Each has an owning pod and a `may_import` list enforced by Plumbline, with dbt `ref()` treated as
  an import.
- Medallion layers inside each dbt domain: bronze (raw), silver (typed, de-duplicated), gold (published).
- Only `billing` reads other domains, and only their gold models.
- Orchestration schedules only. It may not import dataframe or database libraries.

## Alternatives considered
- **One `models/` tree with no domains:** simpler to start, but no ownership and no way to stop cross-reads.
- **A repository per domain:** strongest isolation, but cross-domain changes need coordinated releases. Too heavy for
  a team of this size.

## Consequences
- Billing changes that need new metering fields go through a metering gold model first.
- Moving a model between domains is an architecture change and needs an ADR.
