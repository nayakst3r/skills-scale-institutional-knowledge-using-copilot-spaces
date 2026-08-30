# Working in this repository

Australian banking ontology with agentic maintenance, a physical model layer,
and the governance to run it inside a regulated institution.

## Run this first

    make gate

Ontology gate, structural contract on both flavours, viewer regression test.
It must pass before and after any change you make. It is a required CI check.

## Two layers, do not confuse them

- **`ontology/`** — 366 classes, 474 object properties, 124 scenarios. What
  things mean. Source of truth for meaning.
- **`model/`** — the same model as physical tables: 366 products, 9,479
  attributes, 622 FKs, ECM and MVM flavours. **Generated.** Never hand-edit
  `model/model.json`; edit `agent/attributes.py`, `agent/attributes_ext.py` or
  `agent/attribute_patterns.py` and run `make model`.

`viewer/bank-ontology.html` embeds its own copy of the model. It is a build
artefact. After any model change run `make viewer`, or CI fails on staleness.

## Confidence is load-bearing

Three levels, and they mean different things:

- `curated` — 74 products, hand-specified against CDR, APRA, ASIC, scheme sources
- `patterned` — 292 products, generated from group and keyword rules,
  **confidence notVerified**, no source behind them
- Scenarios: `validated` (14), `corrected` (13), `notVerified` (97)

**Never promote something to `validated` yourself.** An agent may write
`proposed`. Only a human validates. The audit log detects violations and the
MCP server refuses agent principals on approval tools. This is not decoration —
it is the control that makes the pipeline defensible under CPS 220 and FAR.

## Rules that are not negotiable

1. Every assertion carries a source URL and a retrieval date.
2. Confidence is explicit, never implied by omission.
3. The 124 scenarios are the contract. A change that breaks a traversal fails
   the build. Fix the model or fix the scenario — do not delete the scenario.
4. Structural findings are resolved, not suppressed. Bidirectional edges and
   cycles are demoted to soft references with a stated reason. Deleting a
   relationship to make a gate pass is lying about the domain.
5. Anything touching an obligation, licence, prudential reference or validity
   interval never auto-merges, whatever the source tier.

## Where the work is

Ranked by value:

1. **Replace patterned attributes with sourced detail.** 292 products.
   `prompts/domains.md` prompts 19–23 scope it. Highest value available.
2. **Verify the 97 `notVerified` scenarios** bank by bank.
3. **Populate validity intervals.** `applies_on` currently returns candidates,
   not determinations. Prompt 16.
4. **Resolve `TODO: join key` in `model/metrics/*.sql`.** Joins are inferred
   from ontology edges, not designed. Prompt 23.
5. **Normalise the 474 object properties.** Domains and ranges are the union of
   wherever a relationship was used, not designed.

## Common tasks

    make model         rebuild ECM + MVM from the ontology
    make artefacts     DDL, DBML, metric SQL, tag taxonomy
    make viewer        refresh the embedded viewer payload
    make all           all of the above, then gate

    python -m agent.loop --once --fixture tests/fixture_run.json
    python mcp_servers/ontology_store.py      # stdio MCP server
    python mcp_servers/cdr_products.py

## Traps

- **Two classic `<script>` blocks share one global lexical scope.** A top-level
  `const` in both throws at parse time and the second block silently never runs.
  This shipped once. The attribute block is wrapped in an IIFE; wrap any new
  block too. `tests/viewer_check.js` guards it by executing both blocks in one
  shared context — parsing them separately cannot detect it.
- **The sandbox has no network.** The CDR server is written to the published
  contract but untested live. Check the `x-v` header against current standards.
- **`state/*.jsonl` is runtime state.** Never commit it.
- **No consent-bound CDR data, credentials or bank documents in the repo.**
  See `SECURITY.md`.

## Reading order for context

`README.md` → `model/README.md` → `governance/operating-model.md` →
`CONTRIBUTING.md`. `NOTICE.md` has attribution and the source licensing table,
including which Australian sources may not be wrapped at all.
