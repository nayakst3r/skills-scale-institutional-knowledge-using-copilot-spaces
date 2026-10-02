#!/usr/bin/env python3
"""Architecture fitness functions: the principles in ARCHITECTURE.md, as code.

Runs in pre-commit and CI. Each check returns Violations; any violation fails the build.
To add a principle: write a check_* function, register it in CHECKS, add a test, and
reference it in ARCHITECTURE.md.

Usage:
    python tools/check_principles.py <repo_root>
    python tools/check_principles.py <repo_root> --compat-base origin/main
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

LAYERS = ("bronze", "silver", "gold")
CONTRACT_REQUIRED = ("name", "domain", "layer", "version", "owner", "description", "columns")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass(frozen=True)
class Violation:
    rule: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: [{self.rule}] {self.message}"


# ---------- helpers ----------


def domains(root: Path) -> list[Path]:
    base = root / "domains"
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []


def rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root))


def load_contracts(root: Path) -> dict[Path, dict]:
    out = {}
    for d in domains(root):
        for f in sorted((d / "contracts").glob("*.yaml")):
            out[f] = yaml.safe_load(f.read_text()) or {}
    return out


def sqlx_config(text: str) -> dict[str, str]:
    """Pull schema/name/type out of a Dataform config block (good enough for linting)."""
    block = re.search(r"config\s*\{(.*?)\n\}", text, re.S)
    body = block.group(1) if block else ""
    fields = {}
    for key in ("schema", "name", "type"):
        m = re.search(rf'\b{key}\s*:\s*"([^"]+)"', body)
        if m:
            fields[key] = m.group(1)
    fields["has_assertions"] = "assertions" in body
    return fields


def sql_body(text: str) -> str:
    block = re.search(r"config\s*\{.*?\n\}", text, re.S)
    return text[block.end() :] if block else text


# ---------- checks ----------


def check_contracts_valid(root: Path) -> list[Violation]:
    """P4: every contract is complete, well-formed and filed under the right domain."""
    v = []
    for path, c in load_contracts(root).items():
        r = rel(root, path)
        missing = [k for k in CONTRACT_REQUIRED if k not in c]
        if missing:
            v.append(Violation("contract-valid", r, f"missing keys: {', '.join(missing)}"))
            continue
        if c["domain"] != path.parent.parent.name:
            v.append(Violation("contract-valid", r, f"domain '{c['domain']}' != folder '{path.parent.parent.name}'"))
        if c["layer"] not in LAYERS:
            v.append(Violation("contract-valid", r, f"layer must be one of {LAYERS}"))
        if not SEMVER.match(str(c["version"])):
            v.append(Violation("contract-valid", r, "version must be semver MAJOR.MINOR.PATCH"))
        if path.stem != c["name"]:
            v.append(Violation("contract-valid", r, f"file name must match contract name '{c['name']}'"))
    return v


def check_pii_tagged(root: Path) -> list[Violation]:
    """P11: PII columns carry a BigQuery policy tag."""
    v = []
    for path, c in load_contracts(root).items():
        for col in c.get("columns") or []:
            if col.get("pii") and not col.get("policy_tag"):
                v.append(
                    Violation(
                        "pii-policy-tag", rel(root, path), f"column '{col.get('name')}' is pii but has no policy_tag"
                    )
                )
    return v


def check_transforms(root: Path) -> list[Violation]:
    """P2 layer naming, P3 cross-domain reads, P4 contract exists, P10 assertions, P12 no SELECT *."""
    v = []
    contracts = {(c.get("domain"), c.get("layer"), c.get("name")) for c in load_contracts(root).values()}
    ref_re = re.compile(r'ref\(\s*"(\w+?)_(bronze|silver|gold)"')
    for d in domains(root):
        for f in sorted((d / "transforms").glob("*.sqlx")):
            r, text = rel(root, f), f.read_text()
            cfg = sqlx_config(text)
            schema = cfg.get("schema", "")
            m = re.fullmatch(r"(\w+)_(bronze|silver|gold)", schema)
            if not m or m.group(1) != d.name:
                v.append(
                    Violation("layer-naming", r, f"schema must be '{d.name}_<bronze|silver|gold>', got '{schema}'")
                )
                continue
            layer = m.group(2)
            if (
                cfg.get("type") in ("table", "incremental", "view")
                and (d.name, layer, cfg.get("name")) not in contracts
            ):
                v.append(
                    Violation(
                        "contract-exists", r, f"no contract for {schema}.{cfg.get('name')} in {d.name}/contracts/"
                    )
                )
            if layer in ("silver", "gold") and not cfg["has_assertions"]:
                v.append(Violation("assertions", r, "silver/gold tables need Dataform assertions"))
            body = sql_body(text)
            if layer in ("silver", "gold") and re.search(r"select\s+\*(?!\s*except)", body, re.I):
                v.append(Violation("no-select-star", r, "SELECT * not allowed in silver/gold; list columns"))
            for other, other_layer in ref_re.findall(body):
                if other != d.name and other_layer != "gold":
                    v.append(
                        Violation(
                            "cross-domain-read", r, f"reads {other}_{other_layer}; only other domains' gold is allowed"
                        )
                    )
    return v


HARDCODED = [
    (re.compile(r"gs://[\w.-]+"), "hard-coded GCS bucket"),
    (re.compile(r"\bde-(dev|stg|prod)\b"), "hard-coded environment project"),
    (re.compile(r"`[\w-]+\.\w+\.\w+`"), "fully-qualified table name; use ref()"),
]


def check_no_hardcoded_env(root: Path) -> list[Violation]:
    """P6: code is environment-agnostic."""
    v = []
    for base in ("domains", "libs"):
        for f in sorted((root / base).rglob("*")):
            if f.suffix not in (".py", ".sqlx", ".sql"):
                continue
            for i, line in enumerate(f.read_text().splitlines(), 1):
                for rx, msg in HARDCODED:
                    if rx.search(line):
                        v.append(Violation("no-hardcoded-env", f"{rel(root, f)}:{i}", msg))
    return v


DAG_FORBIDDEN = [
    (re.compile(r"^\s*(import|from)\s+pandas\b", re.M), "pandas in a DAG; move logic to Dataform/Dataflow/libs"),
    (
        re.compile(r"\b(SELECT|INSERT\s+INTO|MERGE\s+INTO|DELETE\s+FROM|CREATE\s+TABLE)\b"),
        "SQL in a DAG; move it to a .sqlx transform",
    ),
]


def check_dags_orchestrate_only(root: Path) -> list[Violation]:
    """P8: DAGs schedule and wire tasks; they don't transform."""
    v = []
    for d in domains(root):
        for f in sorted((d / "dags").glob("*.py")):
            text = f.read_text()
            for rx, msg in DAG_FORBIDDEN:
                if rx.search(text):
                    v.append(Violation("dag-orchestration-only", rel(root, f), msg))
    return v


def check_no_sa_keys(root: Path) -> list[Violation]:
    """P11: no service-account keys in the repo (CI uses Workload Identity Federation)."""
    return [
        Violation("no-sa-keys", rel(root, f), "service-account key committed")
        for f in sorted(root.rglob("*.json"))
        if ".git" not in f.parts and '"private_key"' in f.read_text(errors="ignore")
    ]


CHECKS = [
    check_contracts_valid,
    check_pii_tagged,
    check_transforms,
    check_no_hardcoded_env,
    check_dags_orchestrate_only,
    check_no_sa_keys,
]


# ---------- contract compatibility (P5) ----------


def _ver(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in str(s).split("."))


def compat_violations(path: str, old: dict, new: dict) -> list[Violation]:
    """Compare a contract against its previous version on the base branch."""
    v = []
    old_cols = {c["name"]: c for c in old.get("columns", [])}
    new_cols = {c["name"]: c for c in new.get("columns", [])}
    breaking = []
    for name, oc in old_cols.items():
        nc = new_cols.get(name)
        if nc is None:
            breaking.append(f"column '{name}' removed")
        elif nc.get("type") != oc.get("type"):
            breaking.append(f"column '{name}' type {oc.get('type')} -> {nc.get('type')}")
        elif oc.get("mode", "NULLABLE") == "NULLABLE" and nc.get("mode") == "REQUIRED":
            breaking.append(f"column '{name}' NULLABLE -> REQUIRED")
    added_required = [n for n, c in new_cols.items() if n not in old_cols and c.get("mode") == "REQUIRED"]
    breaking += [f"new column '{n}' is REQUIRED (must be NULLABLE)" for n in added_required]

    for b in breaking:
        v.append(
            Violation(
                "contract-compat",
                path,
                f"breaking change: {b}. Create {new.get('name')}_v{_ver(old['version'])[0] + 1}.yaml instead (P5)",
            )
        )
    if old_cols != new_cols and _ver(new.get("version", "0.0.0")) <= _ver(old.get("version", "0.0.0")):
        v.append(Violation("contract-compat", path, "columns changed but version was not bumped"))
    return v


def check_compat_against(root: Path, base: str) -> list[Violation]:
    v = []
    for path, new in load_contracts(root).items():
        r = rel(root, path)
        repo_path = (
            subprocess.run(
                ["git", "-C", str(root), "ls-files", "--full-name", r], capture_output=True, text=True
            ).stdout.strip()
            or r
        )
        res = subprocess.run(["git", "-C", str(root), "show", f"{base}:{repo_path}"], capture_output=True, text=True)
        if res.returncode != 0:
            continue  # new contract: nothing to be compatible with
        v += compat_violations(r, yaml.safe_load(res.stdout) or {}, new)
    return v


def run(root: Path, compat_base: str | None = None) -> list[Violation]:
    if compat_base:
        return check_compat_against(root, compat_base)
    return [x for check in CHECKS for x in check(root)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path)
    ap.add_argument("--compat-base", help="git ref to compare contracts against, e.g. origin/main")
    args = ap.parse_args()
    violations = run(args.root.resolve(), args.compat_base)
    for x in violations:
        print(x)
    print(f"\n{'FAIL' if violations else 'OK'}: {len(violations)} architecture violation(s)")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
