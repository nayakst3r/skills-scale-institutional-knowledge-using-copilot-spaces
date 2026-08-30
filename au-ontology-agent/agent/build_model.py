"""Emit the model in the Databricks industry-data-model shape, localised for Australia.

Their shape:  domains -> sub-domains -> products (tables) -> attributes (+FKs, metric views, tags)
Ours:         groups  -> classes                          -> attributes (+FKs, metric views, tags)

Two flavours, as they ship: ECM (every class) and MVM (the join-heavy core).
"""
from __future__ import annotations
import json, re
from pathlib import Path
from agent.attributes import SPEC as SPEC_CORE, AUDIT
from agent.attributes_ext import EXT
from agent.attribute_patterns import patterned

SPEC = {**SPEC_CORE, **EXT}

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "ontology" / "bank-ontology.json").read_text())

SNAKE = lambda s: re.sub(r"[^a-z0-9]+", "_",
                         re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()).strip("_")

CLASSIFICATIONS = ("pii", "sensitive", "regulatory", "financial", "reference", "derived")


def default_attributes(cid: str, label: str, group: str, fk_targets) -> tuple[str, list]:
    """No curated spec: generate a plausible column set from group and keyword
    rules. Marked 'patterned', confidence notVerified. Not designed detail."""
    pid = SNAKE(cid)
    return f"{pid}_id", patterned(pid, label, group, fk_targets)


def build():
    classes = {c["id"]: c for c in SRC["classes"]}
    groups = {g["id"]: g for g in SRC["groups"]}

    # ---- outbound FK targets per class, needed before columns are generated ----
    edge_targets = {}
    for sc in SRC["scenarios"]:
        for st in sc["steps"]:
            if st["subject"] == st["object"]:
                continue
            tgt = SNAKE(st["object"])
            edge_targets.setdefault(st["subject"], [])
            pair = (tgt, f"{tgt}_id")
            if pair not in edge_targets[st["subject"]]:
                edge_targets[st["subject"]].append(pair)

    # ---- products (tables) with attributes ----
    products, attr_total, curated = [], 0, 0
    for c in SRC["classes"]:
        spec = SPEC.get(c["id"])
        stub = spec is None
        pk, cols = (spec if spec else
                    default_attributes(c["id"], c["label"], c["group"],
                                       edge_targets.get(c["id"], [])))
        if not stub:
            cols = cols + AUDIT
            curated += 1
        attrs = []
        for i, (name, typ, nullable, cdr, efs, cls, src) in enumerate(cols):
            attrs.append({
                "name": name, "type": typ, "nullable": nullable == "Y",
                "primaryKey": name == pk, "ordinal": i + 1,
                "cdrField": cdr, "efsDimension": efs,
                "classification": cls, "sourceSystem": src,
            })
        attr_total += len(attrs)
        products.append({
            "productId": SNAKE(c["id"]), "classId": c["id"], "name": c["label"],
            "domain": c["group"], "domainLabel": groups[c["group"]]["label"],
            "primaryKey": pk, "attributeCount": len(attrs), "attributes": attrs,
            "detail": "curated" if not stub else "patterned",
            "confidence": "notVerified" if stub else "curated",
            "tags": sorted({a["classification"] for a in attrs}),
        })

    # ---- foreign keys, derived from the ontology's object properties ----
    fks, seen = [], set()
    for sc in SRC["scenarios"]:
        for st in sc["steps"]:
            key = (st["subject"], st["object"], st["predicate"])
            if key in seen or st["subject"] == st["object"]:
                continue
            seen.add(key)
            fks.append({
                "name": f'fk_{SNAKE(st["subject"])}__{SNAKE(st["object"])}__{st["predicate"]}',
                "fromProduct": SNAKE(st["subject"]), "toProduct": SNAKE(st["object"]),
                "predicate": st["predicate"], "predicateLabel": st["predicateLabel"],
                "crossDomain": classes[st["subject"]]["group"] != classes[st["object"]]["group"],
            })

    # ---- resolve ontology edges into a physical FK graph ----
    # An ontology tolerates bidirectional edges and cycles. A physical model does
    # not. Rather than suppress the finding, demote the weaker edge to a soft
    # reference: still in the model, not a declared constraint.
    def rank(pid: str) -> int:
        """Lower rank owns the key. Reference and party data are parents;
        events and regulatory artefacts are children."""
        order = {"party":0,"role":1,"prod":2,"scheme":2,"prov":2,"body":2,
                 "dep":3,"credit":3,"mkt":3,"ins":3,"asset":4,"place":4,
                 "loy":5,"event":6,"reg":7}
        cid = next((p["classId"] for p in products if p["productId"] == pid), None)
        return order.get(classes[cid]["group"], 9) if cid else 9

    pairset = {(f["fromProduct"], f["toProduct"]) for f in fks}
    for f in fks:
        a, b = f["fromProduct"], f["toProduct"]
        f["constraint"] = "foreignKey"
        if (b, a) in pairset:                       # bidirectional pair
            if (rank(a), a) > (rank(b), b):
                f["constraint"] = "softReference"
                f["reason"] = "bidirectional pair; other direction owns the key"

    # break residual cycles by demoting the highest-rank back-edge
    def cycles(edges):
        adj = {}
        for e in edges:
            adj.setdefault(e["fromProduct"], set()).add(e["toProduct"])
        seen, stack, found = set(), [], []
        def dfs(v, path):
            seen.add(v); path.append(v)
            for w in adj.get(v, ()):
                if w in path:
                    found.append(path[path.index(w):] + [w])
                elif w not in seen:
                    dfs(w, path)
            path.pop()
        for v in list(adj):
            if v not in seen: dfs(v, [])
        return found

    for _ in range(30):
        live = [f for f in fks if f["constraint"] == "foreignKey"]
        cyc = cycles(live)
        if not cyc: break
        c = cyc[0]
        edges = [(c[i], c[i+1]) for i in range(len(c)-1)]
        worst = max(edges, key=lambda e: (rank(e[0]), e[0]))
        for f in fks:
            if (f["fromProduct"], f["toProduct"]) == worst and f["constraint"] == "foreignKey":
                f["constraint"] = "softReference"
                f["reason"] = "cycle break; ontology edge retained as a soft reference"
                break

    # ---- metric views, from the regulatory bundles ----
    metrics = []
    for sc in SRC["scenarios"]:
        touched = sorted({s["subject"] for s in sc["steps"]} | {s["object"] for s in sc["steps"]})
        metrics.append({
            "name": f'mv_{SNAKE(sc["id"])}',
            "scenarioId": sc["id"], "label": sc["label"], "domain": sc["category"],
            "products": [SNAKE(t) for t in touched],
            "regulatoryReferences": sc["regulatoryReferences"],
            "validation": sc["validation"],
        })

    # ---- MVM: the join-heavy core, their rule ----
    degree = {}
    for f in fks:
        degree[f["fromProduct"]] = degree.get(f["fromProduct"], 0) + 1
        degree[f["toProduct"]] = degree.get(f["toProduct"], 0) + 1
    curated_ids = {SNAKE(k) for k in SPEC}
    mvm_ids = {p["productId"] for p in products
               if p["productId"] in curated_ids or degree.get(p["productId"], 0) >= 4}
    # pull in the immediate neighbours of curated products so nothing is orphaned
    for f in fks:
        if f["fromProduct"] in curated_ids: mvm_ids.add(f["toProduct"])
        if f["toProduct"] in curated_ids: mvm_ids.add(f["fromProduct"])

    model = {
        "modelName": "au-banking", "flavour": "ecm", "version": "v1",
        "localisation": "Australia",
        "shapeCredit": "structure follows databricks-industry-solutions/lakehouse-industry-data-models",
        "counts": {
            "domains": len(groups), "products": len(products), "attributes": attr_total,
            "foreignKeys": sum(1 for f in fks if f["constraint"] == "foreignKey"),
            "softReferences": sum(1 for f in fks if f["constraint"] == "softReference"),
            "crossDomainForeignKeys": sum(f["crossDomain"] for f in fks),
            "metricViews": len(metrics), "curatedProducts": curated,
            "stubProducts": len(products) - curated,
            "avgAttributesPerProduct": round(attr_total / len(products), 1),
            "avgFksPerProduct": round(len(fks) / len(products), 2),
        },
        "domains": [{"domainId": g["id"], "name": g["label"],
                     "productCount": sum(1 for p in products if p["domain"] == g["id"])}
                    for g in SRC["groups"]],
        "products": products, "foreignKeys": fks, "metricViews": metrics,
        "mvmProductIds": sorted(mvm_ids),
    }

    (ROOT / "model").mkdir(exist_ok=True)
    (ROOT / "model" / "model.json").write_text(json.dumps(model, indent=2))

    mvm = dict(model, flavour="mvm",
               products=[p for p in products if p["productId"] in mvm_ids],
               foreignKeys=[f for f in fks
                            if f["fromProduct"] in mvm_ids and f["toProduct"] in mvm_ids])
    mvm["counts"] = dict(model["counts"],
                         products=len(mvm["products"]),
                         attributes=sum(p["attributeCount"] for p in mvm["products"]),
                         foreignKeys=len(mvm["foreignKeys"]))
    (ROOT / "model" / "model.mvm.json").write_text(json.dumps(mvm, indent=2))
    return model, mvm


if __name__ == "__main__":
    ecm, mvm = build()
    c = ecm["counts"]
    print(f'ECM  domains {c["domains"]}  products {c["products"]}  attributes {c["attributes"]}'
          f'  FKs {c["foreignKeys"]} ({c["crossDomainForeignKeys"]} cross-domain)'
          f'  metric views {c["metricViews"]}')
    print(f'     curated {c["curatedProducts"]}  stub {c["stubProducts"]}'
          f'  avg attrs/product {c["avgAttributesPerProduct"]}  avg FKs/product {c["avgFksPerProduct"]}')
    m = mvm["counts"]
    print(f'MVM  products {m["products"]}  attributes {m["attributes"]}  FKs {m["foreignKeys"]}'
          f'  ({round(100*m["products"]/c["products"])}% of ECM by table count)')
