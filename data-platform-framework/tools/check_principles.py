#!/usr/bin/env python3
"""Architecture fitness functions: the principles in ARCHITECTURE.md, as code.

Stack-neutral: the same checks run on every stack. The selected stack (`stack.yaml`, written by
`scripts/use-stack.sh`) only adds its own patterns for hard-coded environments.

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
MODEL_NAME = re.compile(r"^([a-z]+)_(bronze|silver|gold)_([a-z0-9_]+)$")


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


def load_stack(root: Path) -> dict:
    f = root / "stack.yaml"
    return (yaml.safe_load(f.read_text()) or {}) if f.exists() else {}


def load_contracts(root: Path) -> dict[Path, dict]:
    out = {}
    for d in domains(root):
        for f in sorted((d / "contracts").glob("*.yaml")):
            out[f] = yaml.safe_load(f.read_text()) or {}
    return out


def models(root: Path) -> list[tuple[Path, Path]]:
    """(domain_dir, model_file) for every dbt SQL model."""
    return [(d, f) for d in domains(root) for f in sorted((d / "models").glob("*.sql"))]


def strip_jinja_and_comments(sql: str) -> str:
    sql = re.sub(r"\{#.*?#\}", " ", sql, flags=re.S)
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"\{%.*?%\}", " ", sql, flags=re.S)
    return re.sub(r"\{\{.*?\}\}", " __jinja__ ", sql, flags=re.S)


def cte_names(sql: str) -> set[str]:
    return {m.lower() for m in re.findall(r"\b(\w+)\s+as\s*\(", sql, re.I)}


def config_call(sql: str) -> str:
    m = re.search(r"\{\{\s*config\((.*?)\)\s*\}\}", sql, re.S)
    return m.group(1) if m else ""


def tested_models(domain_dir: Path) -> set[str]:
    """Model names that have at least one dbt data test (model- or column-level)."""
    out = set()
    for f in (domain_dir / "models").glob("*.yml"):
        for m in (yaml.safe_load(f.read_text()) or {}).get("models") or []:
            cols = m.get("columns") or []
            if m.get("data_tests") or m.get("tests") or any(c.get("data_tests") or c.get("tests") for c in cols):
                out.add(m.get("name"))
    return out


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
    """P11: PII columns carry a policy tag (mapped to the stack's masking/tagging feature)."""
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


def check_models(root: Path) -> list[Violation]:
    """P2 naming, P3 cross-domain reads, P4 contract exists, P6 ref/source only, P10 tests, P12 no SELECT *."""
    v = []
    contracts = {(c.get("domain"), c.get("layer"), c.get("name")) for c in load_contracts(root).values()}
    tested = {d: tested_models(d) for d in domains(root)}
    for d, f in models(root):
        r, raw = rel(root, f), f.read_text()
        m = MODEL_NAME.match(f.stem)
        if not m or m.group(1) != d.name:
            v.append(
                Violation("model-naming", r, f"model file must be named '{d.name}_<bronze|silver|gold>_<table>.sql'")
            )
            continue
        layer, table = m.group(2), m.group(3)
        if (d.name, layer, table) not in contracts:
            v.append(Violation("contract-exists", r, f"no {layer} contract '{table}' in domains/{d.name}/contracts/"))
        if layer in ("silver", "gold") and f.stem not in tested[d]:
            v.append(
                Violation("data-tests", r, f"silver/gold models need dbt data tests in domains/{d.name}/models/*.yml")
            )
        if re.search(r"\b(schema|alias)\s*=", config_call(raw)):
            v.append(Violation("model-naming", r, "don't set schema/alias in config(); macros/naming.sql derives them"))

        # P3: only other domains' gold
        for other, other_layer in re.findall(r"\bref\(\s*['\"]([a-z]+)_(bronze|silver|gold)_", raw) + re.findall(
            r"\bsource\(\s*['\"]([a-z]+)_(bronze|silver|gold)['\"]", raw
        ):
            if other != d.name and other_layer != "gold":
                v.append(
                    Violation(
                        "cross-domain-read", r, f"reads {other}_{other_layer}; only other domains' gold is allowed"
                    )
                )

        sql = strip_jinja_and_comments(raw)
        ctes = cte_names(sql)
        # P6: every relation comes from ref()/source() or a CTE
        for mm in re.finditer(r"\b(from|join)\s+([A-Za-z_`\"\[][\w.`\"\[\]-]*)", sql, re.I):
            name = mm.group(2)
            before = sql[max(0, mm.start() - 60) : mm.start()]
            if (
                name == "__jinja__"
                or name.lower() in ctes
                or re.search(r"(extract|substring|trim)\s*\([^()]*$", before, re.I)
            ):
                continue
            v.append(Violation("ref-or-source", r, f"reads '{name}' directly; use ref() or source()"))
        # P12: no SELECT * from tables (from a CTE is fine)
        if layer in ("silver", "gold"):
            for mm in re.finditer(r"select\s+(?:distinct\s+)?\*\s*(?:,[^;]*?)?\bfrom\s+(\w+)", sql, re.I | re.S):
                if mm.group(1).lower() not in ctes:
                    v.append(Violation("no-select-star", r, "SELECT * from a table in silver/gold; list the columns"))
    return v


BASE_HARDCODED = [
    (r"(?i)\b(?:password|secret|token)\s*[:=]\s*['\"][^'\"{]{6,}", "hard-coded credential"),
]


def check_no_hardcoded_env(root: Path) -> list[Violation]:
    """P6/P11: code is environment-agnostic and holds no credentials. Patterns come from stack.yaml."""
    patterns = BASE_HARDCODED + [(p["pattern"], p["message"]) for p in load_stack(root).get("forbidden_literals", [])]
    compiled = [(re.compile(p), msg) for p, msg in patterns]
    v = []
    files = [f for d in domains(root) for sub in ("models", "orchestration") for f in sorted((d / sub).rglob("*"))]
    files += sorted((root / "libs").rglob("*.py")) + sorted((root / "macros").rglob("*.sql"))
    for f in files:
        if f.suffix not in (".py", ".sql", ".yml", ".yaml", ".json"):
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            for rx, msg in compiled:
                if rx.search(line):
                    v.append(Violation("no-hardcoded-env", f"{rel(root, f)}:{i}", msg))
    return v


ORCHESTRATION_FORBIDDEN = [
    (re.compile(r"^\s*(import|from)\s+pandas\b", re.M), "pandas in orchestration; move logic into a dbt model"),
    (
        re.compile(r"\b(SELECT|INSERT\s+INTO|MERGE\s+INTO|DELETE\s+FROM|CREATE\s+(OR\s+REPLACE\s+)?TABLE)\b"),
        "SQL in orchestration; move it into a dbt model",
    ),
]


def check_orchestration_only(root: Path) -> list[Violation]:
    """P8: orchestration files schedule and wire dbt; they don't transform."""
    v = []
    for d in domains(root):
        for f in sorted((d / "orchestration").rglob("*")):
            if f.is_file():
                text = f.read_text()
                for rx, msg in ORCHESTRATION_FORBIDDEN:
                    if rx.search(text):
                        v.append(Violation("orchestration-only", rel(root, f), msg))
    return v


def check_no_secrets_files(root: Path) -> list[Violation]:
    """P11: no key files in the repo (CI uses OIDC)."""
    v = []
    for f in sorted(root.rglob("*")):
        if ".git" in f.parts or not f.is_file() or "target" in f.parts:
            continue
        if f.suffix in (".pem", ".p8", ".pfx", ".key"):
            v.append(Violation("no-secrets", rel(root, f), "key file committed"))
        elif f.suffix == ".json" and '"private_key"' in f.read_text(errors="ignore"):
            v.append(Violation("no-secrets", rel(root, f), "service-account key committed"))
    return v


CHECKS = [
    check_contracts_valid,
    check_pii_tagged,
    check_models,
    check_no_hardcoded_env,
    check_orchestration_only,
    check_no_secrets_files,
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
    root = args.root.resolve()
    stack = load_stack(root).get("stack")
    if not stack and not args.compat_base:
        print("note: no stack selected (run scripts/use-stack.sh); stack-specific patterns skipped\n")
    violations = run(root, args.compat_base)
    for x in violations:
        print(x)
    print(
        f"\n{'FAIL' if violations else 'OK'}: {len(violations)} architecture violation(s)"
        + (f" [{stack}]" if stack else "")
    )
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
