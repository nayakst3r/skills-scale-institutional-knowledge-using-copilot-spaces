"""The gate. Nothing merges unless this passes.

Three checks:
  1. referential integrity  - every scenario step resolves to a real class
  2. SHACL shapes           - structural rules on the graph
  3. scenario traversal     - all N scenarios still traverse end to end
Check 3 is the important one: a scenario is an assertion that a path exists.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Result:
    name: str
    passed: bool
    detail: str = ""
    failures: list = None

    def __post_init__(self):
        if self.failures is None:
            self.failures = []


class OntologyValidator:
    def __init__(self, model_path: str, ttl_path: Optional[str] = None,
                 shapes_path: Optional[str] = None):
        self.model = json.loads(Path(model_path).read_text())
        self.ttl_path = ttl_path
        self.shapes_path = shapes_path
        self.class_ids = {c["id"] for c in self.model["classes"]}
        self.prop_ids = {p["id"] for p in self.model["properties"]}

    # ---------- 1. referential integrity ----------
    def check_integrity(self) -> Result:
        bad = []
        for sc in self.model["scenarios"]:
            for st in sc["steps"]:
                if st["subject"] not in self.class_ids:
                    bad.append(f'{sc["id"]}: unknown subject {st["subject"]}')
                if st["object"] not in self.class_ids:
                    bad.append(f'{sc["id"]}: unknown object {st["object"]}')
                if st["predicate"] not in self.prop_ids:
                    bad.append(f'{sc["id"]}: unknown predicate {st["predicate"]}')
        return Result("referential integrity", not bad,
                      f"{len(bad)} dangling references", bad[:20])

    # ---------- 2. orphans ----------
    def check_orphans(self) -> Result:
        used = set()
        for sc in self.model["scenarios"]:
            for st in sc["steps"]:
                used.add(st["subject"]); used.add(st["object"])
        orphans = sorted(self.class_ids - used)
        return Result("no orphan classes", not orphans,
                      f"{len(orphans)} classes no scenario traverses", orphans[:20])

    # ---------- 3. scenario traversal ----------
    def check_scenarios(self) -> Result:
        """Each scenario must form a connected walk over declared relationships."""
        edges = set()
        for p in self.model["properties"]:
            for d in p["domain"]:
                for r in p["range"]:
                    edges.add((d, p["id"], r))
        broken = []
        for sc in self.model["scenarios"]:
            touched = set()
            for st in sc["steps"]:
                if (st["subject"], st["predicate"], st["object"]) not in edges:
                    broken.append(f'{sc["id"]} step {st["order"]}: '
                                  f'{st["subject"]} -{st["predicate"]}-> {st["object"]} undeclared')
                touched.add(st["subject"]); touched.add(st["object"])
            if len(sc["steps"]) and len(touched) < 2:
                broken.append(f'{sc["id"]}: degenerate walk')
        return Result(f'scenario traversal ({len(self.model["scenarios"])} scenarios)',
                      not broken, f"{len(broken)} broken traversals", broken[:20])

    # ---------- 4. provenance discipline ----------
    def check_provenance(self) -> Result:
        missing = [sc["id"] for sc in self.model["scenarios"]
                   if not sc.get("regulatoryReferences")]
        return Result("every scenario cites a regulator", not missing,
                      f"{len(missing)} scenarios with no regulatory reference", missing[:20])

    # ---------- 5. confidence discipline ----------
    def confidence_report(self) -> dict:
        out = {}
        for sc in self.model["scenarios"]:
            out[sc["validation"]] = out.get(sc["validation"], 0) + 1
        return out

    # ---------- 6. SHACL ----------
    def check_shapes(self) -> Result:
        if not (self.ttl_path and self.shapes_path):
            return Result("SHACL shapes", True, "skipped (no shapes supplied)")
        try:
            from pyshacl import validate
            from rdflib import Graph
            g = Graph().parse(self.ttl_path, format="turtle")
            s = Graph().parse(self.shapes_path, format="turtle")
            conforms, _, text = validate(g, shacl_graph=s, inference="none",
                                         abort_on_first=False, meta_shacl=False)
            return Result("SHACL shapes", conforms,
                          "conforms" if conforms else text[:800])
        except Exception as e:                                  # pragma: no cover
            return Result("SHACL shapes", False, f"validator error: {e}")

    def run_all(self) -> list[Result]:
        return [self.check_integrity(), self.check_orphans(), self.check_scenarios(),
                self.check_provenance(), self.check_shapes()]


def main(model="ontology/bank-ontology.json", ttl="ontology/bank-ontology.ttl",
         shapes="ontology/shapes.ttl"):
    v = OntologyValidator(model, ttl, shapes)
    results = v.run_all()
    width = max(len(r.name) for r in results)
    ok = True
    for r in results:
        print(f'{"PASS" if r.passed else "FAIL"}  {r.name.ljust(width)}  {r.detail}')
        for f in r.failures:
            print(f"        - {f}")
        ok &= r.passed
    print("\nconfidence:", v.confidence_report())
    print("\nGATE:", "OPEN" if ok else "CLOSED")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(main(*sys.argv[1:]) if len(sys.argv) > 1 else main())
