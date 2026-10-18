"""Scan an existing repository and propose Plumbline shared context from what is actually there.

Everything is inferred from files on disk and git history; nothing is guessed from names alone without saying so.
Output: a JSON inventory (for agents) or a Markdown report (for humans), plus a proposed architecture block whose
`may_import` lists come from the import graph that really exists, with cycles called out instead of hidden.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from . import gate

LANG = {".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
        ".ts": "TypeScript", ".tsx": "TypeScript", ".cs": "C#", ".java": "Java", ".kt": "Kotlin", ".go": "Go",
        ".rb": "Ruby", ".php": "PHP", ".rs": "Rust", ".scala": "Scala", ".swift": "Swift", ".sql": "SQL",
        ".tf": "Terraform", ".bicep": "Bicep", ".sh": "Shell", ".ps1": "PowerShell"}
CODE = {".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".cs", ".java", ".kt", ".go", ".rb", ".php", ".rs",
        ".scala", ".swift"}
IMPORTABLE = {".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "env", "dist", "build", "out", "target", "bin", "obj",
             "__pycache__", ".next", ".nuxt", "coverage", ".tox", ".mypy_cache", ".pytest_cache", "vendor",
             ".plumbline", ".idea", ".vscode", ".terraform"}
TEST_DIR = re.compile(r"(^|/)(tests?|__tests__|spec|specs|e2e|integration_tests)(/|$)", re.I)
TEST_FILE = re.compile(r"(^test_.*|.*_test\.\w+|.*\.(test|spec)\.\w+|.*Tests?\.cs)$")
FRAMEWORKS = {
    "fastapi": "FastAPI", "django": "Django", "flask": "Flask", "sqlalchemy": "SQLAlchemy", "pydantic": "Pydantic",
    "celery": "Celery", "pandas": "pandas", "pyspark": "PySpark", "langchain": "LangChain", "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK", "boto3": "AWS SDK (boto3)", "azure": "Azure SDK", "pytest": "pytest",
    "express": "Express", "next": "Next.js", "react": "React", "vue": "Vue", "@angular/core": "Angular",
    "@nestjs/core": "NestJS", "prisma": "Prisma", "@prisma/client": "Prisma", "typeorm": "TypeORM",
    "mongoose": "Mongoose", "jest": "Jest", "vitest": "Vitest", "aws-cdk-lib": "AWS CDK", "@azure/functions": "Azure Functions",
    # data engineering
    "dbt-core": "dbt", "dbt-duckdb": "dbt-duckdb", "dbt-bigquery": "dbt-bigquery", "dbt-snowflake": "dbt-snowflake",
    "dbt-databricks": "dbt-databricks", "dbt-fabric": "dbt-fabric", "dbt-postgres": "dbt-postgres",
    "dbt-redshift": "dbt-redshift", "dbt-athena-community": "dbt-athena", "apache-airflow": "Airflow",
    "great-expectations": "Great Expectations", "google-cloud-bigquery": "BigQuery client",
    "databricks-sdk": "Databricks SDK", "snowflake-connector-python": "Snowflake connector", "duckdb": "DuckDB",
    "polars": "Polars", "dagster": "Dagster", "prefect": "Prefect",
}
# Folders that hold examples, fixtures or docs, not the system's own modules
NON_SOURCE = {"demo", "demos", "example", "examples", "fixtures", "samples", "sample_data", "seeds", "docs", "doc",
              "test", "tests", "e2e"}
DBT_REF = re.compile(r"""\bref\(\s*['"]([^'"]+)['"]\s*(?:,\s*['"]([^'"]+)['"]\s*)?\)""")
DOCS = ["README.md", "ARCHITECTURE.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
        "SECURITY.md", "AI_POLICY.md", ".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS",
        ".github/pull_request_template.md", ".github/copilot-instructions.md", ".cursorrules"]
ADR_DIRS = ["docs/adr", "docs/adrs", "docs/decisions", "adr", "doc/adr", "docs/architecture/decisions"]
LAYER_HINTS = {
    "domain": "Business entities and rules", "core": "Core business logic", "model": "Data/domain models",
    "models": "Data/domain models", "entities": "Domain entities", "application": "Use cases / orchestration",
    "services": "Service layer", "service": "Service layer", "usecases": "Use cases", "use_cases": "Use cases",
    "api": "HTTP API", "routes": "HTTP routes", "routers": "HTTP routes", "controllers": "Request handlers",
    "handlers": "Request/event handlers", "web": "Web layer", "ui": "User interface", "components": "UI components",
    "pages": "UI pages", "adapters": "Adapters to external systems", "infrastructure": "Infrastructure adapters",
    "infra": "Infrastructure adapters", "db": "Persistence", "database": "Persistence", "repositories": "Persistence",
    "persistence": "Persistence", "clients": "External API clients", "integrations": "Third-party integrations",
    "shared": "Shared utilities", "common": "Shared utilities", "utils": "Utilities", "lib": "Library code",
    "config": "Configuration", "jobs": "Background jobs", "workers": "Background workers", "cli": "Command line",
}


def sh(root: Path, *args: str) -> str:
    try:
        return subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def list_files(root: Path) -> list[str]:
    out = sh(root, "git", "ls-files", "--cached", "--others", "--exclude-standard")
    files = out.splitlines() if out else [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]
    return [f for f in files if not (set(Path(f).parts[:-1]) & SKIP_DIRS) and not f.startswith(".claude/skills/")]


def is_test(rel: str) -> bool:
    return bool(TEST_DIR.search(rel) or TEST_FILE.match(Path(rel).name))


def is_code(rel: str, dbt: bool = False) -> bool:
    """Source code for module detection. In dbt projects, SQL models and domain YAML (contracts, schema) count too."""
    ext = Path(rel).suffix.lower()
    if ext in CODE:
        return True
    return dbt and (ext == ".sql" or (rel.startswith("domains/") and ext in {".yml", ".yaml"}))


# ---------------------------------------------------------------- stack
def detect_stack(root: Path, files: list[str]) -> dict:
    langs = Counter(LANG[Path(f).suffix.lower()] for f in files if Path(f).suffix.lower() in LANG)
    manifests = [f for f in files if Path(f).name in {
        "pyproject.toml", "requirements.txt", "setup.py", "Pipfile", "package.json", "go.mod", "Cargo.toml",
        "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile", "composer.json"} or f.endswith((".csproj", ".sln"))]
    deps: set[str] = set()
    for d in sorted({Path(m).parent for m in manifests}):
        deps |= set(gate.declared_python_deps(root / d))
        deps |= {x.lower() for x in (gate.declared_js_deps(root / d) or set())}
    frameworks = sorted({name for key, name in FRAMEWORKS.items()
                         if key.replace("-", "_") in deps or key in deps or (key == "azure" and any(
                             d.startswith("azure") for d in deps))})
    commands = {}
    for m in sorted(f for f in manifests if Path(f).name == "package.json" and "node_modules" not in f):
        where = Path(m).parent.as_posix()
        prefix = "" if where == "." else f"cd {where} && "
        try:
            scripts = json.loads((root / m).read_text(errors="ignore")).get("scripts", {})
        except json.JSONDecodeError:
            continue
        for k in ("test", "lint", "build", "typecheck", "format"):
            if k in scripts:
                commands.setdefault(f"{k} ({where})" if where != "." else k,
                                    prefix + ("npm test" if k == "test" else f"npm run {k}"))
    mk = root / "Makefile"
    if mk.exists():
        for t in re.findall(r"(?m)^([a-zA-Z][\w-]*):", mk.read_text(errors="ignore")):
            if t in {"test", "lint", "build", "run", "format", "check", "typecheck"}:
                commands.setdefault(t, f"make {t}")
    for m in sorted(f for f in manifests if Path(f).name in {"pyproject.toml", "requirements.txt", "setup.py"}):
        where = Path(m).parent.as_posix()
        if any(f.endswith(".py") and is_test(f) and (where == "." or f.startswith(where + "/")) for f in files):
            commands.setdefault(f"test ({where})" if where != "." else "test",
                                ("" if where == "." else f"cd {where} && ") + "python -m pytest")
    if any(f.endswith(".sln") or f.endswith(".csproj") for f in files):
        commands.setdefault("test", "dotnet test")
        commands.setdefault("build", "dotnet build")
    if (root / "go.mod").exists():
        commands.setdefault("test", "go test ./...")
    dbt_projects = sorted(Path(f).parent.as_posix() for f in files if Path(f).name == "dbt_project.yml")
    if dbt_projects:
        frameworks = sorted(set(frameworks) | {"dbt"})
        commands.setdefault("dbt build", "dbt build")
    infra = sorted({"Terraform" for f in files if f.endswith(".tf")} | {"Bicep" for f in files if f.endswith(".bicep")}
                   | {"Docker" for f in files if Path(f).name.startswith("Dockerfile")}
                   | {"Kubernetes/Helm" for f in files if "/templates/" in f and f.endswith((".yaml", ".yml"))
                      and any(Path(x).name == "Chart.yaml" for x in files)})
    return {"languages": dict(langs.most_common()), "manifests": manifests, "frameworks": frameworks,
            "dependency_count": len(deps), "commands": commands, "infrastructure": infra, "dbt_projects": dbt_projects}


# ---------------------------------------------------------------- modules
def source_roots(files: list[str], dbt: bool = False) -> list[str]:
    code = [f for f in files if is_code(f, dbt) and not is_test(f) and Path(f).parts[0].lower() not in NON_SOURCE]
    if not code:
        return []
    tops = Counter(Path(f).parts[0] for f in code if len(Path(f).parts) > 1)
    total = len(code)
    preferred = {"src", "app", "lib", "packages", "services", "apps", "backend", "frontend", "server", "client", "api",
                 "web", "domains", "modules", "pipelines", "dags"}
    roots = [t for t, n in tops.most_common() if n / total >= 0.10 or (t in preferred and n / total >= 0.03)]
    if dbt and "domains" in tops and "domains" not in roots:
        roots.insert(0, "domains")  # domain-oriented dbt layout: domains/<domain>/ is the architecture
    loose = sum(1 for f in code if len(Path(f).parts) == 1)
    if loose / total >= 0.3:
        roots.append(".")
    return roots[:6] or ["."]


def candidate_modules(files: list[str], roots: list[str], dbt: bool = False) -> list[dict]:
    """A module = a directory under a source root (descending through single-package wrappers) holding code."""
    code = [f for f in files if is_code(f, dbt) and not is_test(f)]
    mods: list[dict] = []
    for root in roots:
        base = Path(root)
        inside = [Path(f) for f in code if root == "." or f.startswith(root + "/")]
        depth = len(base.parts) if root != "." else 0
        # descend while everything sits in one sub-directory (e.g. src/<package>/...); every domain is a module
        while root != "domains":
            subdirs = {p.parts[depth] for p in inside if len(p.parts) > depth + 1}
            loose = [p for p in inside if len(p.parts) == depth + 1 and p.name not in {"__init__.py", "index.ts",
                                                                                    "index.js", "main.py"}]
            if len(subdirs) == 1 and not loose:
                depth += 1
                continue
            break
        prefix = "/".join(inside[0].parts[:depth]) if inside and depth else (root if root != "." else "")
        groups: dict[str, list[str]] = defaultdict(list)
        for p in inside:
            key = p.parts[depth] if len(p.parts) > depth + 1 else "(root files)"
            groups[key].append(p.as_posix())
        markers = {"__init__.py", "index.ts", "index.js", "py.typed"}
        if all(Path(m).name in markers for m in groups.get("(root files)", ["x"])):
            groups.pop("(root files)", None)  # package markers alone don't make a module
        for name, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            if name == "(root files)":
                glob = f"{prefix}/*" if prefix else "*"
                mod_name = f"{Path(prefix).name}_root" if prefix else "root"
            else:
                glob = f"{prefix}/{name}/**" if prefix else f"{name}/**"
                # a bare "src"/"lib" folder is better named after what contains it (frontend/src -> frontend)
                mod_name = Path(prefix).name if name in {"src", "lib", "source"} and prefix else name
            children = Counter(Path(m).parts[depth + 1] for m in members if len(Path(m).parts) > depth + 2)
            mods.append({"name": re.sub(r"[^a-zA-Z0-9_-]", "_", mod_name).lower(), "paths": [glob],
                         "files": len(members), "hint": LAYER_HINTS.get(name.lower(), ""), "root_files": name ==
                         "(root files)", "subfolders": [c for c, _ in children.most_common(8)] if len(members) >= 15 else []})
    # de-duplicate names across roots
    seen = Counter()
    for m in mods:
        seen[m["name"]] += 1
        if seen[m["name"]] > 1:
            m["name"] = f"{m['name']}_{seen[m['name']]}"
    return mods


def import_graph(root: Path, files: list[str], mods: list[dict], roots: list[str]) -> dict:
    arch = gate.Architecture({"source_roots": [r for r in roots if r != "."],
                              "module": [{"name": m["name"], "paths": m["paths"]} for m in mods]})
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    local_top = {Path(f).parts[0].lower() for f in files} | {
        Path(f).parts[1].lower() for f in files if len(Path(f).parts) > 1 and Path(f).parts[0] in roots}
    edges: Counter = Counter()
    examples: dict[tuple, str] = {}
    packages: dict[str, Counter] = defaultdict(Counter)
    unplaced = []
    sql_index = {Path(f).stem: f for f in files if f.endswith(".sql")}
    for rel in files:
        ext = Path(rel).suffix.lower()
        if ext == ".sql" and not is_test(rel):  # dbt: ref('model') is a dependency on the module owning that model
            src = arch.module_of(rel)
            if not src:
                continue
            try:
                text = (root / rel).read_text(errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                for a, b in DBT_REF.findall(line):
                    target_file = sql_index.get(b or a)
                    tgt = arch.module_of(target_file) if target_file else None
                    if tgt and tgt.name != src.name:
                        edges[(src.name, tgt.name)] += 1
                        examples.setdefault((src.name, tgt.name), f"{rel}:{i}")
            continue
        if ext not in IMPORTABLE or is_test(rel):
            continue
        src = arch.module_of(rel)
        if not src:
            if ext in CODE and Path(rel).name not in {"__init__.py", "index.ts", "index.js", "__main__.py"}:
                unplaced.append(rel)
            continue
        try:
            text = (root / rel).read_text(errors="ignore")
        except OSError:
            continue
        imps = gate.python_imports(text, rel, arch.source_roots) if ext == ".py" else gate.js_imports(
            text.splitlines(), rel)
        for line, pkg, cands in imps:
            tgt = next((t for t in (arch.module_of(c) for c in cands if not pkg or gate.exists_in_repo(root, c)) if t), None)
            if tgt and tgt.name != src.name:
                edges[(src.name, tgt.name)] += 1
                examples.setdefault((src.name, tgt.name), f"{rel}:{line}")
            elif not tgt and pkg and pkg not in stdlib and pkg not in local_top and not pkg.startswith((".", "@/", "~")):
                packages[src.name][pkg] += 1
    graph = defaultdict(set)
    for a, b in edges:
        graph[a].add(b)
    return {"edges": [{"from": a, "to": b, "imports": n, "example": examples[(a, b)]}
                      for (a, b), n in edges.most_common()],
            "cycles": find_cycles(graph), "packages": {m: dict(c.most_common(12)) for m, c in packages.items()},
            "unplaced_code": unplaced[:50]}


def find_cycles(graph: dict[str, set]) -> list[list[str]]:
    """Strongly connected components with more than one node (Tarjan)."""
    index, low, stack, on, out, i = {}, {}, [], set(), [], [0]

    def visit(v):
        index[v] = low[v] = i[0]
        i[0] += 1
        stack.append(v)
        on.add(v)
        for w in graph.get(v, ()):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(sorted(comp))

    for v in list(graph):
        if v not in index:
            visit(v)
    return out


# ---------------------------------------------------------------- context
def existing_context(root: Path, files: list[str]) -> dict:
    present = {d: (root / d).exists() for d in DOCS}
    adrs = [f for f in files if any(f.startswith(d + "/") for d in ADR_DIRS) and f.endswith(".md")]
    owners = {}
    for co in (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"):
        p = root / co
        if p.exists():
            for ln in p.read_text(errors="ignore").splitlines():
                parts = ln.split("#")[0].split()
                if len(parts) >= 2:
                    owners[parts[0]] = parts[1:]
            break
    ci = []
    for wf in sorted((root / ".github/workflows").glob("*.y*ml")) if (root / ".github/workflows").exists() else []:
        text = wf.read_text(errors="ignore")
        jobs = re.findall(r"(?m)^  ([\w-]+):\s*$", text.split("jobs:", 1)[1]) if "jobs:" in text else []
        ci.append({"file": wf.relative_to(root).as_posix(), "jobs": jobs,
                   "runs_tests": bool(re.search(r"(?i)\b(test|pytest|jest|vitest|dotnet test|go test)\b", text))})
    for f in ("azure-pipelines.yml", ".gitlab-ci.yml", "Jenkinsfile", "bitbucket-pipelines.yml"):
        if (root / f).exists():
            ci.append({"file": f, "jobs": [], "runs_tests": None})
    tests = [f for f in files if is_test(f) and Path(f).suffix.lower() in CODE]
    return {"docs": present, "adrs": adrs, "codeowners": owners, "ci": ci, "test_files": len(tests)}


def ignored_sources(root: Path, files: list[str], stack: dict) -> list[dict]:
    """Source files the repo's .gitignore would silently drop — e.g. a template's `*.sql` hiding every dbt model."""
    probes: set[str] = set()
    for m in stack["manifests"]:
        d = Path(m).parent
        name = Path(m).name
        if name in {"pyproject.toml", "requirements.txt", "setup.py", "Pipfile"}:
            probes.add((d / "plumbline_probe.py").as_posix())
        elif name == "package.json":
            probes |= {(d / "src/plumbline_probe.ts").as_posix(), (d / "src/plumbline_probe.js").as_posix()}
        elif name.endswith(".csproj"):
            probes.add((d / "PlumblineProbe.cs").as_posix())
        elif name == "go.mod":
            probes.add((d / "plumbline_probe.go").as_posix())
    for d in stack.get("dbt_projects", []):
        base = Path(d)
        probes |= {(base / "models/plumbline_probe.sql").as_posix(), (base / "macros/plumbline_probe.sql").as_posix(),
                   (base / "tests/plumbline_probe.sql").as_posix()}
        prefix = "" if d == "." else d + "/"
        doms = sorted({Path(f[len(prefix):]).parts[1] for f in files
                       if f.startswith(prefix + "domains/") and len(Path(f[len(prefix):]).parts) > 2})
        for dom in doms[:3]:
            probes.add((base / "domains" / dom / "models" / "plumbline_probe.sql").as_posix())
    if any(f.endswith(".tf") for f in files):
        probes.add("platform/terraform/plumbline_probe.tf")
    found = []
    for probe in sorted(p.removeprefix("./") for p in probes):
        out = sh(root, "git", "check-ignore", "-v", "--", probe).strip()
        if out and "\t" in out:
            src, path = out.split("\t", 1)
            source, line, pattern = src.rsplit(":", 2) if src.count(":") >= 2 else (src, "?", "?")
            if pattern.startswith("!"):
                continue
            found.append({"path": path.replace("plumbline_probe", "*").replace("PlumblineProbe", "*"),
                          "pattern": pattern, "source": f"{source}:{line}"})
    return found


def existing_guardrails(root: Path, files: list[str]) -> dict:
    """What the repo already enforces, so adoption integrates with it instead of duplicating or replacing it."""
    g: dict = {"hook_manager": None, "hooks": [], "fitness_functions": [], "branch_protection_scripts": [],
               "agent_context": []}
    pc = root / ".pre-commit-config.yaml"
    if pc.exists():
        g["hook_manager"] = "pre-commit"
        g["hooks"] = re.findall(r"(?m)^\s*-?\s*id:\s*([\w.-]+)", pc.read_text(errors="ignore"))
        g["hooks"] += [h["id"] for h in re.finditer(r"\{\s*id:\s*([\w.-]+)", pc.read_text(errors="ignore"))
                       for h in [{"id": h.group(1)}]]
    elif any((root / n).exists() for n in ("lefthook.yml", ".lefthook.yml", "lefthook.yaml")):
        g["hook_manager"] = "lefthook"
    elif (root / ".husky").is_dir():
        g["hook_manager"] = "husky"
    texts = [(root / f).read_text(errors="ignore") for f in files
             if f.startswith(".github/workflows/") or Path(f).name in {"Makefile", "justfile", "Taskfile.yml"}]
    for t in texts:
        for cmd in re.findall(r"(?:python3?|node|bash|sh)?\s*\.?/?((?:tools|scripts|ci)/[\w./-]*(?:check|lint|validate|verify|principle|guard)[\w./-]*)", t):
            if cmd not in g["fitness_functions"] and (root / cmd).exists():
                g["fitness_functions"].append(cmd)
    for f in files:
        if f.startswith("scripts/") and f.endswith((".sh", ".py", ".ps1")):
            t = (root / f).read_text(errors="ignore")
            if re.search(r"rulesets|branches/[^ ]*/protection|required_status_checks|merge.queue", t):
                g["branch_protection_scripts"].append(f)
        if f.startswith((".github/instructions/", ".github/agents/", ".github/prompts/", ".cursor/rules/")) or \
                f in {".github/copilot-instructions.md", "GEMINI.md", "CLAUDE.md", "AGENTS.md", ".cursorrules"}:
            g["agent_context"].append(f)
    g["hooks"] = sorted(set(g["hooks"]))
    return g


def git_activity(root: Path) -> dict:
    authors = sh(root, "git", "log", "--since=90.days", "--format=%ae").split()
    commits = sh(root, "git", "rev-list", "--count", "HEAD").strip()
    hot = Counter(f for f in sh(root, "git", "log", "--since=90.days", "--name-only", "--format=").split() if f)
    trailers = Counter(t.strip().lower() or "missing" for t in sh(
        root, "git", "log", "-200", "--format=%(trailers:key=AI-Assisted,valueonly)%x00").split("\x00")[:-1])
    return {"commits": int(commits) if commits.isdigit() else 0, "active_authors_90d": len(set(authors)),
            "hot_files_90d": [f for f, _ in hot.most_common(10)], "ai_trailers_last_200": dict(trailers)}


# ---------------------------------------------------------------- proposal
def propose_block(mods: list[dict], graph: dict, roots: list[str], owners: dict) -> str:
    cyclic = {m for c in graph["cycles"] for m in c}
    allowed = defaultdict(set)
    for e in graph["edges"]:
        allowed[e["from"]].add(e["to"])
    lines = ["source_roots = " + json.dumps([r for r in roots if r != "."] or ["."]),
             "strict_placement = false        # existing repo: tighten to true once stray code has a home",
             "architecture_owners = []        # e.g. [\"@org/architects\"] — confirm with the team", ""]
    for m in mods:
        note = []
        if m["name"] in cyclic:
            note.append("in an import cycle — see scan report; decide the intended direction")
        if m["hint"]:
            note.append(m["hint"])
        mod_owners = sorted({o for pat, os_ in owners.items() for o in os_
                             if any(g.rstrip("*").rstrip("/").lstrip("/") in pat.lstrip("/") or
                                    pat.lstrip("/").rstrip("*").rstrip("/") in g for g in m["paths"])})
        lines += ["[[module]]", f'name = "{m["name"]}"' + (f"    # {'; '.join(note)}" if note else ""),
                  "paths = " + json.dumps(m["paths"]),
                  "may_import = " + json.dumps(sorted(allowed[m["name"]])) + "    # observed today",
                  "owners = " + json.dumps(mod_owners), ""]
    return "\n".join(lines).rstrip() + "\n"


def scan(root: Path) -> dict:
    root = gate.repo_root(root)
    files = list_files(root)
    stack = detect_stack(root, files)
    dbt = bool(stack["dbt_projects"])
    roots = source_roots(files, dbt)
    mods = candidate_modules(files, roots, dbt)
    graph = import_graph(root, files, mods, roots)
    ctx = existing_context(root, files)
    result = {"root": str(root), "files": len(files), "stack": stack, "source_roots": roots,
              "modules": mods, "graph": graph, "context": ctx, "git": git_activity(root),
              "ignored_sources": ignored_sources(root, files, stack), "guardrails": existing_guardrails(root, files)}
    result["proposed_architecture_block"] = propose_block(mods, graph, roots, ctx["codeowners"])
    result["_files"] = files
    result["gaps"] = gaps(result)
    del result["_files"]
    return result


def gaps(r: dict) -> list[str]:
    g, docs = [], r["context"]["docs"]
    template_dirs = {"overlay", "overlays", "template", "templates", "skeleton", "starter", "example", "examples", "demo"}
    nested = sorted({f.split("/.github/")[0] for f in r.get("_files", []) if "/.github/" in f
                     and not f.startswith(".github/")
                     and not template_dirs & set(Path(f.split("/.github/")[0]).parts)})  # copied into place by design
    for n in nested:
        g.append(f"CRITICAL: {n}/.github/ is not at the repository root — GitHub ignores its workflows, CODEOWNERS, "
                 "templates and Copilot instructions there. Move it to the root or make the folder its own repository")
    for i in r.get("ignored_sources", []):
        g.append(f"CRITICAL: `{i['pattern']}` in {i['source']} git-ignores {i['path']} — these files are never committed")
    for d in ("ARCHITECTURE.md", "AGENTS.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "AI_POLICY.md"):
        if not docs.get(d):
            g.append(f"No {d}")
    if not any(docs.get(c) for c in (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")):
        g.append("No CODEOWNERS — review isn't routed to owners")
    if not r["context"]["adrs"]:
        g.append("No architecture decision records")
    if not r["context"]["ci"]:
        g.append("No CI pipeline found")
    elif not any(c.get("runs_tests") for c in r["context"]["ci"]):
        g.append("CI doesn't appear to run tests")
    if r["context"]["test_files"] == 0:
        g.append("No test files found")
    for c in r["graph"]["cycles"]:
        g.append(f"Import cycle between modules: {' <-> '.join(c)}")
    if r["graph"]["unplaced_code"]:
        g.append(f"{len(r['graph']['unplaced_code'])} code file(s) outside the detected modules")
    return g


def to_markdown(r: dict) -> str:
    s = r["stack"]
    out = [f"# Repository scan — {Path(r['root']).name}", "",
           f"{r['files']} files · {r['git']['commits']} commits · {r['git']['active_authors_90d']} active authors (90 days)", "",
           "## Stack", f"- Languages: {', '.join(f'{k} ({v})' for k, v in s['languages'].items()) or 'none detected'}",
           f"- Frameworks: {', '.join(s['frameworks']) or 'none detected'}",
           f"- Manifests: {', '.join(s['manifests']) or 'none'}",
           f"- Infrastructure: {', '.join(s['infrastructure']) or 'none detected'}",
           f"- Commands: {', '.join(f'{k}: `{v}`' for k, v in s['commands'].items()) or 'none detected'}", "",
           f"## Candidate modules (source roots: {', '.join(r['source_roots']) or 'none'})", "",
           "| Module | Paths | Files | Looks like | Could split into |", "|---|---|---|---|---|"]
    out += [f"| {m['name']} | `{', '.join(m['paths'])}` | {m['files']} | {m['hint'] or '—'} | "
            f"{', '.join(m.get('subfolders') or []) or '—'} |" for m in r["modules"]]
    out += ["", "## Dependencies between modules (observed imports)", ""]
    if r["graph"]["edges"]:
        out += ["| From | To | Imports | Example |", "|---|---|---|---|"]
        out += [f"| {e['from']} | {e['to']} | {e['imports']} | `{e['example']}` |" for e in r["graph"]["edges"]]
    else:
        out.append("No cross-module imports detected (or languages not yet analysed: only Python and JS/TS imports are traced).")
    if r["graph"]["cycles"]:
        out += ["", "**Cycles:** " + "; ".join(" ↔ ".join(c) for c in r["graph"]["cycles"])]
    out += ["", "## Existing shared context",
            "- Docs present: " + (", ".join(d for d, v in r["context"]["docs"].items() if v) or "none"),
            f"- ADRs: {len(r['context']['adrs'])}", f"- Test files: {r['context']['test_files']}",
            "- CI: " + ("; ".join(f"{c['file']} ({', '.join(c['jobs']) or 'jobs?'})" for c in r["context"]["ci"]) or "none"),
            "", "## Existing guardrails (integrate with these; don't duplicate or replace them)",
            f"- Git hook manager: {r['guardrails']['hook_manager'] or 'none'}"
            + (f" — hooks: {', '.join(r['guardrails']['hooks'])}" if r['guardrails']['hooks'] else ""),
            f"- Fitness functions run in CI/Makefile: {', '.join(r['guardrails']['fitness_functions']) or 'none found'}",
            f"- Branch-protection scripts: {', '.join(r['guardrails']['branch_protection_scripts']) or 'none'}",
            f"- Agent context files: {len(r['guardrails']['agent_context'])}"
            + (f" ({', '.join(r['guardrails']['agent_context'][:6])}{', …' if len(r['guardrails']['agent_context']) > 6 else ''})"
               if r['guardrails']['agent_context'] else ""),
            "", "## Gaps", *([f"- {g}" for g in r["gaps"]] or ["- None found"]),
            "", "## Proposed architecture block (draft — describes the code as it is today; humans decide the target)",
            "", "```toml plumbline-architecture", r["proposed_architecture_block"].rstrip(), "```"]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="plumbline scan", description="Inventory an existing repo for adoption")
    ap.add_argument("--root", default=".")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--output", "-o")
    a = ap.parse_args(argv)
    r = scan(Path(a.root).resolve())
    body = json.dumps(r, indent=2) if a.format == "json" else to_markdown(r)
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True)
        Path(a.output).write_text(body)
        print(f"plumbline: scan written to {a.output}")
    else:
        print(body)
    return 0
