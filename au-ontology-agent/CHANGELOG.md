# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The model is versioned as a product, not a project.

## [Unreleased]
### Fixed
- `mcp_servers/cdr_products.py` and `data/sources.yaml` sent `x-v: 4` to every
  CDR banking endpoint from one shared header value. The three endpoints
  version independently and were three versions apart: Get Data Holder Brands
  Summary is at v2, Get Products at v5 (v4 retired 2026-08-10), Get Product
  Detail at v7 (v6 retired 2026-08-10, v4 - the value the code was sending -
  retired 2025-11-10). Split into per-endpoint headers pinned to the version
  each endpoint is actually on, sourced against the Consumer Data Standards
  spec and endpoint-version schedule, retrieved 2026-08-30. **Not yet
  confirmed against a live data holder response** - this sandbox has no
  network path to `api.cdr.gov.au` or any data holder host, so the CDR path
  is still unverified end to end. Re-check the moment that's possible.

## [0.3.0]
### Added
- Physical model layer in `model/`, following the Databricks
  industry-data-model shape: 366 products, 9,479 attributes, 622 foreign keys,
  124 metric views, ECM and MVM flavours.
- Pattern generator (`agent/attribute_patterns.py`) — group and keyword rules
  producing joinable column sets for products without a curated spec.
- Structural contract (`agent/model_gates.py`) matching the Databricks integrity
  checks, plus two Australian gates: curated products must carry an APRA
  reporting dimension, and PII-carrying products are reported.
- Artefact exports: `schemas/` DDL, `diagram/model.dbml`, `metrics/` SQL,
  `ontology/tag-taxonomy.json`.
- Attribute drill-down in the viewer, and a model stat bar.
- MCP tools: `get_attributes`, `find_by_cdr_field`,
  `find_by_regulatory_dimension`, `pii_report`, `attribute_coverage`.
- Attribute-level prompts 19–23.

### Fixed
- Viewer threw `Identifier 'panel' has already been declared` — two classic
  script blocks share one global lexical scope, so the second block never ran
  and the drill-down was silently dead. The attribute block is now wrapped in
  an IIFE.

### Changed
- Third detail level introduced: `curated`, `patterned`, `stub`. `stub` is no
  longer used; the old stubs became `patterned` with confidence `notVerified`.
- Bidirectional and cycle-forming ontology edges are demoted to soft references
  rather than deleted — 23 edges, each carrying its reason.

## [0.2.0]
### Added
- Governance layer: operating model and RACI, FAR accountability statement
  draft, CPS 230 tolerance levels.
- Hash-chained audit log with segregation-of-duties detection.
- Risk-based change-class policy replacing the binary auto-merge check.
- OAuth 2.1 resource-server controls per MCP authorization spec 2025-11-25.
- Source licensing and wrappability recorded per source.

## [0.1.0]
### Added
- Ontology: 366 classes, 474 object properties, 124 scenarios across 15 groups.
- Validation gate: referential integrity, orphans, scenario traversal,
  regulatory citation, SHACL shapes.
- MCP servers for the ontology store and CDR product reference data.
- Agent loop: watcher, differ, proposer, validator, router.
