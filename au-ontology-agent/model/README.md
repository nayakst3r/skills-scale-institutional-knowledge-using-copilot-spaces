# Physical model — Databricks industry-data-model shape, localised

Structure follows
[databricks-industry-solutions/lakehouse-industry-data-models](https://github.com/databricks-industry-solutions/lakehouse-industry-data-models):
Domain → Product (table) → Attribute (column), with foreign keys, metric views,
governance tags, two flavours and a structural contract. Their banking v1 is
19 domains / 501 tables / 19,792 attributes; this is the Australian localisation
of the same shape, generated from the ontology.

|  | ECM | MVM |
|---|---|---|
| Domains | 15 | 15 |
| Products | 366 | 286 |
| Attributes | 9,479 | 7,211 |
| Foreign keys | 622 | 547 |
| Metric views | 124 | 124 |
| Curated products | 74 | 74 |
| Pattern-generated | 292 | 212 |

MVM is 78% of ECM by product count — the curated core plus every product with
four or more relationships, and the immediate neighbours of anything curated so
nothing is orphaned.

## Structural contract — both flavours CLEAN

    PASS  dangling FKs                            0
    PASS  self-FKs on primary keys                0
    PASS  bidirectional FK pairs                  0
    PASS  FK cycles (graph SCC)                   0
    PASS  siloed products                         0
    PASS  cross-domain duplicate product names    0
    PASS  products without a primary key          0
    PASS  AU: curated products with no APRA dimension  0
    INFO  AU: ontology edges demoted to soft references  23
    INFO  AU: products carrying PII                     241

## The ontology-to-physical problem

An ontology tolerates bidirectional edges and cycles — `kyc verifies person`
and `person identified via kyc` are both true. A physical FK graph cannot.

Rather than suppress the finding, the build demotes the weaker edge to a
**soft reference**: still in the model, not a declared constraint. Direction is
decided by rank — party and reference data own keys; events and regulatory
artefacts are children. 23 edges were demoted, each carrying its reason.

This is the honest answer. A model that reported zero cycles by deleting
relationships would be lying about the domain.

## Australian bindings on every attribute

| Field | Meaning |
|---|---|
| `cdrField` | The CDR banking payload field, where one exists |
| `efsDimension` | The APRA EFS / ARF dimension it feeds — loan purpose, borrower type, ANZSIC, resident/non-resident, security type, rate type |
| `classification` | pii, sensitive, regulatory, financial, reference, derived |
| `sourceSystem` | Where it typically originates |

Two additional gates beyond the Databricks contract: a curated product with no
APRA reporting dimension fails, and PII-carrying products are reported so they
cannot be missed.

## Honest limit

Three detail levels, and the distinction is the point:

| Level | Products | Meaning |
|---|---|---|
| `curated` | 74 | Hand-specified against CDR, APRA, ASIC and scheme sources |
| `patterned` | 292 | Generated from group and keyword rules — plausible, joinable, **confidence notVerified** |
| `stub` | 0 | No longer used |

**Pattern-generated columns are not designed detail.** They come from the group
the class sits in and keywords in its label: a class in Credit & Security gets
loan purpose, borrower type, ANZSIC, rate type, risk weight and arrears bucket;
anything whose label contains "card" gets scheme, interchange category and a
dual-network flag; anything matching "alert" or "sanction" gets a detection rule,
an investigator, an escalation flag and a tipping-off restriction. Foreign key
columns are added from the ontology edges so the model actually joins.

The viewer draws them with a dashed outline and says so in the panel. Prompts
19–23 in `prompts/domains.md` replace them with sourced detail.

Curated coverage now spans all 15 groups: party and roles, deposits, credit,
markets, insurance, card schemes, providers, regulators, loyalty, events, assets,
location and the regulatory objects.

    python -m agent.build_model      # regenerate both flavours
    python -m agent.model_gates model/model.json
    python -m agent.model_gates model/model.mvm.json
