# ADR-0001: Medallion layering on BigQuery with Dataform

- **Status:** Accepted
- **Date:** 2026-10-02
- **Deciders:** Architecture Guild

## Context
Ten engineers across three domains need a consistent way to land, clean, and publish data
without stepping on each other. Options considered: dbt on BigQuery, Dataform, and Spark on
Dataproc.

## Decision
- BigQuery is the warehouse; datasets are named `<domain>_<layer>` with layer ∈ {bronze, silver, gold}.
- Transforms are written in Dataform SQLX (native to GCP, managed in BigQuery Studio, no extra runtime).
- Only `gold` is readable outside the owning domain, through authorized views.
- Dataproc is used only for workloads BigQuery can't handle, and needs its own ADR.

## Consequences
- One transform language for everyone, which makes AI-generated SQL more consistent.
- Owners can refactor bronze and silver freely.
- Cross-domain needs require the producing domain to publish gold, which adds coordination but protects stability.

## Enforcement
`check_principles.py`: `layer_naming`, `cross_domain_reads`, `contract_exists`. BigQuery IAM
in `platform/terraform` grants cross-domain readers access to `*_gold` only.
