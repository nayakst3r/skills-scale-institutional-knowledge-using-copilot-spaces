## What and why
<!-- One concern per PR. Link the issue. -->
Closes #

## Domain / scope
- [ ] sales  - [ ] finance  - [ ] customer  - [ ] platform / libs (separate PR!)

## Contracts touched
<!-- List contracts/*.yaml changed, or "none". -->

## Breaking change?
- [ ] No: additive only
- [ ] Yes: new contract major version and `_vN` table; consumers notified; deprecation date: ____

## How I tested
- [ ] `make check` and `make local-build` pass locally (sample data added for new sources)
- [ ] Ran in my cloud sandbox (`sbx_<user>_*`), with a link to the query or result
- [ ] dbt data tests added or updated

## Principles
- [ ] Idempotent and re-runnable (P7)
- [ ] Partition filter on large tables (P12)
- [ ] Needs Architecture Guild review (add the `needs-architecture` label)

## AI assistance
- [ ] Used AI; I've reviewed and can explain every line. Tool(s): ____
