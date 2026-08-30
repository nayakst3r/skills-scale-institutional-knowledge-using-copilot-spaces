# NOTICE

## Structural attribution

The physical model layer in `model/` follows the structural pattern of
**[databricks-industry-solutions/lakehouse-industry-data-models](https://github.com/databricks-industry-solutions/lakehouse-industry-data-models)**
— the Domain → Product → Attribute hierarchy, ECM and MVM flavours, foreign keys,
metric views, governance tags, the shipped artefact set (`schemas/`, `diagram/`,
`metrics/`, `ontology/`) and the structural integrity contract (FK cycles,
bidirectional pairs, dangling FKs, self-FKs, silos, cross-domain duplicate names).

**No model content is copied from that repository.** Every class, attribute,
relationship, scenario and regulatory binding here is Australian and was authored
for this project. The shape is borrowed; the contents are not.

> **Unverified:** that repository's `LICENSE.md` was not retrieved when this was
> built. Its README states the models are "auto-generated and provided as-is for
> reference." Before publishing, read their licence and confirm that structural
> reuse with attribution is permitted. If it is not, the pattern must be
> re-derived or the attribution strengthened to whatever the licence requires.

## Data sources

Nothing in this repository redistributes third-party data. Sources are wrapped
at runtime or cited. Licences as recorded in `data/sources.yaml`:

| Source | Licence | Wrappable |
|---|---|---|
| Consumer Data Standards (CDR) | MIT | yes — endpoints are mandated public |
| GLEIF LEI | CC0 1.0 | yes |
| Federal Register of Legislation | CC BY 4.0 | yes |
| ASIC registers via data.gov.au | CC BY | yes |
| ABN Lookup | Web Services Agreement, per-client GUID | with care |
| RBA statistics | CC BY 4.0 | with care — Cash Rate has special conditions |
| APRA registers, standards, statistics | site terms, unverified | with care |
| AUSTRAC registers | no open licence found | **no** |
| AFCA Datacube | no stated reuse licence | **no** |
| State land titles registries | state government, broker-gated | **no** |
| Visa / Mastercard scheme rules | proprietary | **no** |
| Bank PDS / TMD / key facts | bank copyright | **no** — cite and link only |
| CDR consumer data | consent-bound | requires CDR accreditation |

## Regulatory references

References to APRA prudential and reporting standards, ASIC regulatory guides,
AUSTRAC rules, RBA payment standards, the ABA Banking Code, ARNECC requirements
and Australian legislation are **citations, not reproductions**. The instruments
themselves are not included. Always read the current instrument; several cited
here have commencement dates in 2026 and 2027 and were not in force when written.

## Accuracy

This model is a working artefact, not a compliance product.

- **74 of 366 products carry curated attributes.** The other 292 are
  pattern-generated and carry confidence `notVerified`.
- **97 of 124 scenarios are `notVerified`** — authored from research, not
  validated bank by bank.
- **Validity intervals are stubs.** `applies_on` returns candidates, not
  determinations.
- Per-bank applicability assessments are analytical judgements, not measurements.

Verify against primary sources and your own organisation's position before any
use that carries consequence.
