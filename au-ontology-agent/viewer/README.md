# Viewer

`bank-ontology.html` — the scenario explorer. Open it in a browser; no server,
no build step, no dependencies.

## What it is

The same model as `ontology/bank-ontology.json`, rendered as a radial graph.
15 sectors, 366 classes, 124 scenarios. Pick a scenario and the graph dims
everything else and zooms to just that subgraph, with the steps numbered in
order and the regulatory bundle listed beside it.

- **Filter by bank** — Westpac, ANZ, NAB, CBA, ING, Macquarie. Chips turn green,
  amber, red or grey for applicable, varies, not applicable, unverified.
- **Filter by regulator** — APRA, ASIC, AUSTRAC, RBA/AP+, CDR, ATO, ABA Code,
  AFCA, PPSR, State/ECNL, Housing Australia.
- **Labels toggle** — 366 nodes will not fit at full zoom, so labels are hidden
  until you pick a scenario or hover a node.

## Keeping it in step with the ontology

The HTML embeds its own copy of the model as JS arrays. It is a **view**, not the
source of truth — `ontology/bank-ontology.json` is. If the agent pipeline changes
the model, the viewer goes stale until it is regenerated.

Treat it as a build artefact: regenerate from the JSON after any merged batch,
or replace it with a viewer that fetches from the ontology store MCP server.
Until then, check the class and scenario counts in the viewer against
`describe_ontology` before showing it to anyone.
