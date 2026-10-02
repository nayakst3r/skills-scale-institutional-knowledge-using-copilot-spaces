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
- [ ] Ran in my sandbox (`sbx_<user>_*`), with a link to the query or result
- [ ] Dataform assertions added or updated
- [ ] `make check` passes locally

## Principles
- [ ] Idempotent and re-runnable (P7)
- [ ] Partition filter on large tables (P12)
- [ ] Needs Architecture Guild review (add the `needs-architecture` label)

## AI assistance
- [ ] Used AI; I've reviewed and can explain every line. Tool(s): ____
