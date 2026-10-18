"""plumbline command-line interface.

    plumbline scan       inventory an existing repo: stack, modules, real import graph, gaps, proposed architecture
    plumbline init       scaffold shared context, gates, CI and the /plumbline skill into a repo
    plumbline check      run the quality gate (all gate flags pass through: --diff, --staged, --all, --format ...)
    plumbline doctor     verify a repo's Plumbline setup is complete and consistent
    plumbline rules      list built-in and custom rules
    plumbline worktree   new <issue> | list | remove <issue> | prune — one isolated worktree per issue
    plumbline hooks      generate lefthook.yml from the detected stack (--write, --install)
    plumbline codeowners regenerate CODEOWNERS from ARCHITECTURE.md
    plumbline clients    add /plumbline for Copilot, Gemini CLI and Antigravity (also done by init)
    plumbline install    install the /plumbline skill for your agent (user or project scope)
    plumbline hook       Claude Code PostToolUse hook entry point (quality gate on each file the agent writes)
    plumbline guard      Claude Code PreToolUse hook entry point (blocks merge/approve/push-to-main/--no-verify)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import clients, gate, guard, hooks, scaffold, scan, worktree

USAGE = __doc__


# ---------------------------------------------------------------- install
def install(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="plumbline install", description="Install the /plumbline skill")
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--project", action="store_true", help="install into ./.claude/skills (shared via git)")
    scope.add_argument("--dir", help="install into <DIR>/plumbline (any agent that reads Agent Skills folders)")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args(argv)
    if a.dir:
        dest = Path(a.dir).expanduser() / "plumbline"
    elif a.project:
        dest = Path.cwd() / ".claude/skills/plumbline"
    else:
        dest = Path.home() / ".claude/skills/plumbline"
    if a.uninstall:
        if dest.exists():
            shutil.rmtree(dest)
            print(f"Removed {dest}")
        else:
            print(f"Nothing installed at {dest}")
        return 0
    scaffold.copy_skill(dest)
    print(f"Installed /plumbline {gate.VERSION} -> {dest}")
    print("Restart your agent, then run:  /plumbline init")
    return 0


# ---------------------------------------------------------------- doctor
def doctor(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="plumbline doctor", description="Check a repository's Plumbline setup")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    root = gate.repo_root(Path(a.root).resolve())
    checks: list[tuple[str, str, str]] = []  # (status, check, detail)

    def ok(name, detail=""):
        checks.append(("ok", name, detail))

    def bad(name, detail):
        checks.append(("fail", name, detail))

    def warn(name, detail):
        checks.append(("warn", name, detail))

    (ok if sys.version_info >= (3, 11) else bad)("Python 3.11+", sys.version.split()[0])
    (ok if (root / ".git").exists() else bad)("Git repository", str(root))

    vend = root / ".plumbline/plumbline.py"
    if not vend.exists():
        bad("Vendored gate", "missing .plumbline/plumbline.py - run `plumbline init`")
    else:
        m = re.search(r'VERSION = "([^"]+)"', vend.read_text(errors="ignore"))
        v = m.group(1) if m else "?"
        (ok if v == gate.VERSION else warn)("Vendored gate", f"version {v}" + ("" if v == gate.VERSION else
                                            f" (this CLI is {gate.VERSION}; run `plumbline init` to update)"))

    try:
        cfg = gate.load_config(root)
        ok("plumbline.toml", "parsed" if (root / "plumbline.toml").exists() else "not present - using defaults")
    except Exception as e:  # tomllib error types vary
        bad("plumbline.toml", f"invalid: {e}")
        cfg = gate.load_config(Path("/nonexistent"))

    arch, err = gate.Architecture.load(root, cfg)
    if arch:
        mods = ", ".join(m.name for m in arch.modules)
        ok("Architecture block", f"{len(arch.modules)} modules: {mods}")
    else:
        bad("Architecture block", err)

    sc = gate.Scanner(root, cfg)
    sc.governance()
    if sc.findings:
        by_file: dict[str, list] = {}
        for f in sc.findings:
            by_file.setdefault(f.path, []).append(f)
        for path, fs in by_file.items():
            lines = ",".join(str(f.line) for f in fs if f.line)
            detail = fs[0].message if len(fs) == 1 else f"{len(fs)} unfinished sections (lines {lines})"
            bad("Shared context", f"{path}: {detail}")
    else:
        ok("Shared context", f"{len(cfg['required_docs'])} required docs present and finished")

    lh = next((root / n for n in ("lefthook.yml", ".lefthook.yml", "lefthook.yaml") if (root / n).exists()), None)
    hooks_path = subprocess.run(["git", "config", "core.hooksPath"], cwd=root, capture_output=True, text=True).stdout.strip()
    pc_cfg = root / ".pre-commit-config.yaml"
    if pc_cfg.exists() and not lh:
        hooks_dir = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=root, capture_output=True,
                                   text=True).stdout.strip() or ".git/hooks"
        pc_hook = (root / hooks_dir / "pre-commit") if not Path(hooks_dir).is_absolute() else Path(hooks_dir) / "pre-commit"
        installed = pc_hook.exists() and "pre-commit" in pc_hook.read_text(errors="ignore")
        has_gate = "plumbline-gate" in pc_cfg.read_text(errors="ignore")
        if installed and has_gate:
            ok("Git hooks", "pre-commit framework active, Plumbline gate included")
        elif not has_gate:
            warn("Git hooks", "pre-commit framework in use but the Plumbline gate isn't in .pre-commit-config.yaml - "
                              "run `plumbline init` (it adds a local hook)")
        else:
            warn("Git hooks", "pre-commit hooks not installed in this clone - run `pre-commit install "
                              "--hook-type pre-commit --hook-type commit-msg`")
    elif lh:
        git_hooks = Path(subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=root, capture_output=True,
                                        text=True).stdout.strip() or ".git/hooks")
        pc = (root / git_hooks / "pre-commit") if not git_hooks.is_absolute() else git_hooks / "pre-commit"
        if pc.exists() and "lefthook" in pc.read_text(errors="ignore"):
            ok("Git hooks", f"Lefthook active ({lh.name})")
        else:
            warn("Git hooks", "lefthook.yml present but not installed in this clone - run `make setup` (lefthook install)")
        if hooks.MARKER in lh.read_text(errors="ignore"):
            m = re.search(r"run: (.+?) --staged", lh.read_text(errors="ignore"))
            fresh = hooks.lefthook_yaml(root, m.group(1) if m else "python3 .plumbline/plumbline.py",
                                        branch=scaffold.default_branch(root))
            if fresh != lh.read_text():
                warn("Hook jobs", "stack changed since lefthook.yml was generated - run `plumbline hooks --write`")
            else:
                ok("Hook jobs", "match the detected stack")
        run_mjs = root / ".plumbline/hooks/run.mjs"
        if run_mjs.exists():
            node = shutil.which("node")
            if not node:
                bad("TypeScript hooks", "Node.js not found — install Node >= 22.18 (or 22.6+ / any Node with npx tsx)")
            else:
                r = subprocess.run([node, str(run_mjs), "--check"], cwd=root, capture_output=True, text=True)
                tpl = hooks.TS_TEMPLATES / ".plumbline/hooks/lib.mts"
                stale = (root / ".plumbline/hooks/lib.mts").read_text() != tpl.read_text()
                (warn if stale or r.returncode else ok)(
                    "TypeScript hooks", (r.stdout.strip() or r.stderr.strip()) +
                    (" — library outdated, run `plumbline hooks --write`" if stale else ""))
    elif hooks_path == ".githooks" and os.access(root / ".githooks/pre-commit", os.X_OK):
        ok("Git hooks", ".githooks active")
    else:
        warn("Git hooks", "not active in this clone - run `make setup`")

    settings = root / ".claude/settings.json"
    stext = settings.read_text() if settings.exists() else ""
    if "PostToolUse" in stext and "plumbline" in stext:
        ok("Agent quality hook", "PostToolUse checks every file the agent writes")
    else:
        bad("Agent quality hook", "no Plumbline PostToolUse hook in .claude/settings.json")
    if "PreToolUse" in stext and "guard" in stext:
        ok("Human-review guard", "PreToolUse blocks merge/approve/push-to-main/--no-verify")
    else:
        bad("Human-review guard", "no PreToolUse guard in .claude/settings.json - run `plumbline init`")

    skill = root / ".claude/skills/plumbline/SKILL.md"
    (ok if skill.exists() else warn)("Project skill", ".claude/skills/plumbline" if skill.exists()
                                     else "not vendored - teammates must install /plumbline themselves")

    # Other coding agents: thin entry points to the same skill (plumbline clients)
    have = []
    if (root / ".github/prompts/plumbline-check.prompt.md").exists():
        have.append("Copilot (/plumbline-…)")
    gem = root / ".gemini/settings.json"
    if (root / ".gemini/commands/plumbline.toml").exists():
        gem_hooks = gem.exists() and "plumbline-human-review-guard" in gem.read_text()
        have.append("Gemini CLI (/plumbline" + (", hooks)" if gem_hooks else ", no hooks)"))
    if (root / ".agents/skills/plumbline/SKILL.md").exists():
        have.append("Antigravity (/plumbline)")
    (ok if len(have) == 3 else warn)("Other agents", ", ".join(have) if len(have) == 3 else
                                     (", ".join(have) + "; " if have else "") + "run `plumbline clients` to add the rest")

    ruleset_file = root / ".github/rulesets/main-protection.json"
    if ruleset_file.exists():
        rs = json.loads(ruleset_file.read_text())
        pr = next((r.get("parameters", {}) for r in rs.get("rules", []) if r.get("type") == "pull_request"), None)
        gaps = []
        if pr is None:
            gaps.append("no pull_request rule")
        else:
            if pr.get("required_approving_review_count", 0) < 1:
                gaps.append("0 required approvals")
            if not pr.get("require_code_owner_review"):
                gaps.append("code-owner review off")
            if not pr.get("require_last_push_approval"):
                gaps.append("last pusher can approve their own push")
            if not pr.get("dismiss_stale_reviews_on_push"):
                gaps.append("stale approvals survive new pushes")
        if rs.get("bypass_actors"):
            gaps.append("bypass actors configured")
        if gaps:
            bad("Human review", "ruleset does not enforce it: " + "; ".join(gaps))
        else:
            ok("Human review", "human code-owner approval required; no bypass; stale approvals dismissed")
    else:
        warn("Human review", "no ruleset file - human approval is not enforced as code (`/plumbline protect`)")

    wf_dir = root / ".github/workflows"
    ruleset = root / ".github/rulesets/main-protection.json"
    if wf_dir.exists():
        job_names = set()
        for wf in wf_dir.glob("*.y*ml"):
            job_names |= set(re.findall(r"(?m)^\s{4}name:\s*([\w.-]+)\s*$", wf.read_text(errors="ignore")))
        if ruleset.exists():
            data = json.loads(ruleset.read_text())
            needed = {c["context"] for r in data.get("rules", []) if r.get("type") == "required_status_checks"
                      for c in r["parameters"]["required_status_checks"]}
            missing = needed - job_names
            if missing:
                bad("Required checks", f"ruleset requires {sorted(missing)} but no workflow job has that name")
            else:
                ok("Required checks", f"{sorted(needed)} match workflow jobs")
        else:
            warn("Required checks", "no .github/rulesets/main-protection.json")
    elif (root / "pipelines").exists():
        ok("CI", "pipelines/ present (Azure DevOps / GitLab)")
    else:
        bad("CI", "no CI workflow found - run `plumbline init` or `/plumbline ci add`")

    if a.json:
        print(json.dumps([{"status": s, "check": c, "detail": d} for s, c, d in checks], indent=2))
    else:
        icon = {"ok": "✓", "warn": "!", "fail": "✗"}
        for s, c, d in checks:
            print(f" {icon[s]} {c:<20} {d}")
        fails = sum(1 for s, *_ in checks if s == "fail")
        print(f"\n{'Healthy' if not fails else f'{fails} problem(s)'} — plumbline {gate.VERSION}")
    return 1 if any(s == "fail" for s, *_ in checks) else 0


# ---------------------------------------------------------------- rules
def rules(argv: list[str]) -> int:
    root = gate.repo_root(Path(argv[0] if argv else ".").resolve())
    cfg = gate.load_config(root)
    disabled = set(cfg["disabled_rules"])
    print(f"{'ID':<12} {'SEVERITY':<9} {'STATE':<9} RULE")
    for rid, (title, sev) in gate.rule_catalogue(cfg).items():
        sev = cfg["severity_overrides"].get(rid, sev)
        state = "disabled" if rid in disabled else ("custom" if rid not in gate.RULES else "on")
        print(f"{rid:<12} {sev:<9} {state:<9} {title}")
    return 0


# ---------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    try:
        return _main(argv)
    except BrokenPipeError:  # e.g. `plumbline rules | head`
        sys.stderr.close()
        return 0


def _main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print(USAGE)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd in {"-V", "--version", "version"}:
        print(f"plumbline {gate.VERSION}")
        return 0
    if cmd == "check":
        return gate.run(rest)
    if cmd == "hook":
        return gate.run(["--hook", *rest])
    if cmd == "worktree":
        return worktree.main(rest)
    if cmd == "hooks":
        return hooks.main(rest)
    if cmd == "scan":
        return scan.main(rest)
    if cmd == "guard":
        return guard.main()
    if cmd == "init":
        return scaffold.main(rest)
    if cmd == "codeowners":
        return gate.run(["--codeowners", rest[0] if rest else ".github/CODEOWNERS"])
    if cmd == "install":
        return install(rest)
    if cmd == "clients":
        return clients.main(rest)
    if cmd == "doctor":
        return doctor(rest)
    if cmd == "rules":
        return rules(rest)
    print(f"plumbline: unknown command '{cmd}'\n{USAGE}", file=sys.stderr)
    return 2
