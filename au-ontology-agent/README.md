# Australian banking ontology — agentic maintenance scaffold

The ontology, the agents that keep it current, the MCP servers that serve it,
and the governance model that lets a regulated institution run it.

## What is here

| Artefact | Detail |
|---|---|
| `ontology/bank-ontology.ttl` | OWL. 366 classes, 474 object properties, 124 scenarios, 11,133 triples |
| `ontology/bank-ontology.json` | Flat model — easiest ingestion path |
| `ontology/shapes.ttl` | SHACL. Confidence must be explicit; a scenario without a regulator is not a banking scenario |
| `agent/` | validator (the gate), differ, proposer, change policy, audit, auth, loop |
| `mcp_servers/` | ontology store (the only write path) and CDR product reference data |
| `governance/` | operating model and RACI, FAR accountability statement, CPS 230 tolerances |
| `prompts/` | the domain prompt pack for platform execution |
| `data/sources.yaml` | 20 sources, tiered, with licence and wrappability |
| `model/model.json` | Physical model — 366 products, 9,479 attributes, 622 FKs, 124 metric views |
| `model/model.mvm.json` | Minimum viable model — 286 products, 7,211 attributes |
| `model/schemas/` | CREATE TABLE DDL, one file per domain, comments carrying CDR and APRA bindings |
| `model/diagram/model.dbml` | DBML for ER rendering |
| `model/metrics/` | 124 metric view SQL files, one per scenario |
| `model/ontology/tag-taxonomy.json` | Classification taxonomy and handling rules |

## Two layers

**Ontology layer** — 366 classes, 474 object properties, 124 scenarios. What
things mean and how they relate. Lives in `ontology/`.

**Physical layer** — the same model in the Databricks industry-data-model shape
(Domain → Product → Attribute, with FKs, metric views, governance tags, ECM and
MVM flavours). Structure follows
[databricks-industry-solutions/lakehouse-industry-data-models](https://github.com/databricks-industry-solutions/lakehouse-industry-data-models).
Lives in `model/`. See `model/README.md`.

An ontology tolerates bidirectional edges and cycles; a physical FK graph cannot.
The build demotes the weaker edge to a **soft reference** rather than deleting
it — 23 edges, each carrying its reason. Both flavours pass the structural
contract clean.

## The design

No Australian regulator publishes an MCP server. APRA, ASIC, AUSTRAC, the RBA
and AFCA publish APIs, registers and PDFs. The servers here wrap authoritative
sources — "approved body" means the source is authoritative, not the server.

Patterns taken from the precedents that do exist:

- **Neo4j's official server** — read-only enforcement, schema as a first-class tool.
- **SEC EDGAR MCP** — every response carries the source URL and retrieval time.
- **Stripe** — remote server, OAuth, narrow well-named tools.
- **MCP authorization spec 2025-11-25** — resource server only, audience validation
  under RFC 8707, PRM under RFC 9728, S256 PKCE. Pin the revision; it has changed
  three times.

## Source tiers and what may be wrapped

| Tier | Kind | Agent may |
|---|---|---|
| 1 | Authoritative machine-readable — CDR product data, CDR register, APRA/ASIC registers, legislation feed, GLEIF, ABN | assert |
| 2 | Authoritative unstructured — prudential standards, regulatory guides, AUSTRAC rules, RBA papers | propose |
| 3 | Bank-published — PDS, TMD, key facts | propose |
| 4 | Secondary — press, specialist commentary | detect only |

Of 20 registered sources: 6 cleanly wrappable, 6 wrappable with care, 7 not
wrappable, 1 requires CDR accreditation. **GLEIF is CC0. CDR standards are MIT
and the product endpoints are mandated unauthenticated.** Card scheme rules,
land titles, AUSTRAC registers and the AFCA datacube are not wrappable — cite,
do not redistribute.

## The gate

    $ python agent/validator.py
    PASS  referential integrity               0 dangling references
    PASS  no orphan classes                   0 classes no scenario traverses
    PASS  scenario traversal (124 scenarios)  0 broken traversals
    PASS  every scenario cites a regulator    0 with no regulatory reference
    PASS  SHACL shapes                        conforms
    GATE: OPEN

Wire as a required CI check. The scenario suite is the point: a scenario asserts
that a path exists, so a change that breaks one fails the build.

## Change routing

    addClass     tier1  -> additive  auto-merge     tier 1 machine-readable source
    addClass     tier3  -> additive  human-review   source tier 3
    setValidity  tier1  -> semantic  human-review   touches a validity interval
    relabel      tier1  -> editorial auto-merge     editorial only
    retire       tier1  -> breaking  review-board   breaking change to published semantics

High-volume low-risk and low-volume high-consequence take different paths. That
is what makes this automatable without being reckless.

## Controls that actually hold

- **Hash-chained audit log.** Edit any record and `verify()` reports the index it
  broke at. This is the CPS 230 and CPG 235 evidence artefact.
- **Segregation of duties, enforced twice** — at the token (`assert_human` rejects
  an agent principal on approval tools) and in the log (`segregation_breaches()`
  finds a proposer approving its own change).
- **No self-promotion.** An agent may write `proposed`. Only a human moves an
  assertion to `validated`.
- **Provenance on every response.** Source, file, retrieval time, spec revision.

## Governance

`governance/operating-model.md` — RACI, roles, cadence, SLAs, and the control-to-
obligation map: FAR accountable person, CPS 230 tolerances and the 72h/24h
notification windows, CPS 234 asset classification, CPG 235 lineage and quality,
CPS 220 three lines of defence, ISO/IEC 42001 and NIST AI RMF, and the Voluntary
AI Safety Standard's human-oversight guardrail.

The Ontology Product Owner is a named individual and the FAR accountable person.
Not a committee.

## Completing the model

`prompts/domains.md` holds 18 domain prompts for platform execution — products
and sub-products, parties, obligations, validity intervals, scenarios. Every
prompt returns deltas, not prose. `prompts/ingestion.md` has the ingestion rules:
prompt output is tier 2 at best, anything self-marked `validated` gets downgraded
on ingestion, no source URL means no ingestion, and a batch that breaks a
traversal is rejected whole.

## Running

    pip install -r requirements.txt
    python agent/validator.py
    python -m agent.loop --once --fixture tests/fixture_run.json
    python -m agent.build_model             # regenerate ECM + MVM
    python -m agent.model_gates model/model.json
    python -m agent.export_artifacts        # DDL, DBML, metric SQL, tag taxonomy
    python mcp_servers/ontology_store.py
    python mcp_servers/cdr_products.py

## Honest limits

- **97 of 124 scenarios are `notVerified`.** Call `unverified_report` before
  trusting anything.
- **Validity intervals are stubs.** The watcher detects commencement dates; the
  interval model is not populated. `applies_on` returns candidates, not answers.
  Prompt 16 in the pack exists to fix this.
- **474 object properties came from usage, not design.** Domains and ranges are
  the union of wherever a relationship was used. Normalise before production.
- **CDR endpoints untested live** — no network in the build sandbox. Written to
  the published contract; check the `x-v` header against current standards.
- **The ontology store forks nothing yet.** Consider replacing it with the Neo4j
  or GraphDB MCP server and keeping only the gate, the change policy and the
  audit chain — that logic is the part worth owning.
- **What stays human:** whether a new concept is a class, subclass or attribute;
  retiring concepts; two authoritative sources disagreeing; and whether the model
  still matches how the bank actually operates. No feed answers that.

## Licence and attribution

Apache-2.0. See `LICENSE`.

The physical model layer follows the structural pattern of
[databricks-industry-solutions/lakehouse-industry-data-models](https://github.com/databricks-industry-solutions/lakehouse-industry-data-models)
— the hierarchy, flavours, artefact set and integrity contract. No model content
is copied; every class, attribute and scenario here is Australian and was
authored for this project. Their licence was not retrieved when this was built —
read it before publishing. See `NOTICE.md`.

No third-party data is redistributed. Sources are wrapped at runtime or cited,
with licences and wrappability recorded per source in `data/sources.yaml`.

## Repository

    make install       dependencies
    make gate          ontology gate + structural contract + viewer check
    make all           rebuild model, artefacts, viewer, then gate

`CONTRIBUTING.md` has the change classes and the rules that are not negotiable.
`SECURITY.md` has the threat model and what must never be committed.
`CHANGELOG.md` tracks the model as a product.

CI runs the gate, both structural contracts, a reproducibility check that fails
if `model/` is stale, the viewer regression test, and an audit-chain integrity
check on every push and pull request.
