"""Structural integrity gates, matching the Databricks model contract.

Their checks: FK cycles (graph SCC), bidirectional FK pairs, dangling FKs,
self-FKs on primary keys, siloed tables, cross-domain duplicate product names.
All 40 of their MVMs ship with zero findings. Ours should too.
"""
from __future__ import annotations
import json
from pathlib import Path


def load(p): return json.loads(Path(p).read_text())


def gates(model: dict) -> list[dict]:
    prods = {p["productId"]: p for p in model["products"]}
    fks = [f for f in model["foreignKeys"] if f.get("constraint", "foreignKey") == "foreignKey"]
    soft = [f for f in model["foreignKeys"] if f.get("constraint") == "softReference"]
    out = []

    dangling = [f["name"] for f in fks
                if f["fromProduct"] not in prods or f["toProduct"] not in prods]
    out.append({"check": "dangling FKs (target product missing)", "count": len(dangling),
                "examples": dangling[:5]})

    self_fk = [f["name"] for f in fks if f["fromProduct"] == f["toProduct"]]
    out.append({"check": "self-FKs on primary keys", "count": len(self_fk),
                "examples": self_fk[:5]})

    pairs = {(f["fromProduct"], f["toProduct"]) for f in fks}
    bidir = sorted({tuple(sorted(p)) for p in pairs if (p[1], p[0]) in pairs})
    out.append({"check": "bidirectional FK pairs", "count": len(bidir),
                "examples": [f"{a} <-> {b}" for a, b in bidir[:5]]})

    # FK cycles by strongly connected components (Tarjan, iterative)
    adj = {}
    for f in fks:
        adj.setdefault(f["fromProduct"], set()).add(f["toProduct"])
    index, low, onstack, stack, idx, sccs = {}, {}, set(), [], [0], []
    def strongconnect(v):
        work = [(v, iter(adj.get(v, ())))]
        index[v] = low[v] = idx[0]; idx[0] += 1; stack.append(v); onstack.add(v)
        while work:
            node, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = idx[0]; idx[0] += 1
                    stack.append(w); onstack.add(w)
                    work.append((w, iter(adj.get(w, ()))))
                    advanced = True
                    break
                if w in onstack:
                    low[node] = min(low[node], index[w])
            if not advanced:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[node])
                if low[node] == index[node]:
                    comp = []
                    while True:
                        w = stack.pop(); onstack.discard(w); comp.append(w)
                        if w == node: break
                    if len(comp) > 1: sccs.append(comp)
    for v in list(adj):
        if v not in index: strongconnect(v)
    out.append({"check": "FK cycles (graph SCC)", "count": len(sccs),
                "examples": [" -> ".join(c[:4]) for c in sccs[:3]]})

    allf = model["foreignKeys"]
    linked = {f["fromProduct"] for f in allf} | {f["toProduct"] for f in allf}
    silos = sorted(set(prods) - linked)
    out.append({"check": "siloed products (no FK in or out)", "count": len(silos),
                "examples": silos[:5]})

    names = {}
    for p in model["products"]:
        names.setdefault(p["name"].lower(), set()).add(p["domain"])
    dupes = [n for n, d in names.items() if len(d) > 1]
    out.append({"check": "cross-domain duplicate product names", "count": len(dupes),
                "examples": dupes[:5]})

    nopk = [p["productId"] for p in model["products"]
            if not any(a["primaryKey"] for a in p["attributes"])]
    out.append({"check": "products without a primary key", "count": len(nopk),
                "examples": nopk[:5]})

    # Australian additions - not in the Databricks contract
    no_efs = [p["productId"] for p in model["products"]
              if p["detail"] == "curated"
              and not any(a["efsDimension"] for a in p["attributes"])]
    out.append({"check": "AU: curated products with no APRA reporting dimension",
                "count": len(no_efs), "examples": no_efs[:5]})

    out.append({"check": "AU: ontology edges demoted to soft references",
                "count": len(soft), "examples": [f["name"] for f in soft[:5]],
                "informational": True})

    pii = [p["productId"] for p in model["products"] if "pii" in p["tags"]]
    out.append({"check": "AU: products carrying PII (must be classified, not a failure)",
                "count": len(pii), "examples": pii[:5], "informational": True})
    return out


def main(path="model/model.json"):
    m = load(path)
    print(f'{m["modelName"]} {m["flavour"]} — {m["counts"]["products"]} products, '
          f'{m["counts"]["attributes"]} attributes, {m["counts"]["foreignKeys"]} FKs\n')
    fails = 0
    for g in gates(m):
        info = g.get("informational")
        ok = g["count"] == 0 or info
        tag = "INFO" if info else ("PASS" if ok else "FAIL")
        print(f'{tag}  {g["check"]:58} {g["count"]}')
        for e in g["examples"][:3]:
            print(f'        - {e}')
        fails += 0 if ok else 1
    print("\nCONTRACT:", "CLEAN" if not fails else f"{fails} FINDINGS")
    return fails


if __name__ == "__main__":
    import sys
    sys.exit(main(*sys.argv[1:]))
