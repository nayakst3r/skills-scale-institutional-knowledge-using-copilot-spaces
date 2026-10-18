#!/usr/bin/env python3
"""Scaffold Plumbline into a project. Idempotent: never overwrites without --force."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .hooks import (default_branch, install as lefthook_install, install_ts_hooks, is_typescript_repo, lefthook_yaml,
                    wants_lefthook)

HERE = Path(__file__).resolve().parent  # the skill folder is also the python package: SKILL.md, reference/, templates/
SKILL_DIR = HERE
TPL = HERE / "templates"
BEGIN, END = "<!-- plumbline:begin", "<!-- plumbline:end -->"


def detect_ci(root: Path) -> str:
    if (root / ".github").exists():
        return "github"
    if (root / "azure-pipelines.yml").exists() or (root / ".azuredevops").exists():
        return "azure"
    if (root / ".gitlab-ci.yml").exists():
        return "gitlab"
    remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True).stdout
    if "dev.azure.com" in remote or "visualstudio.com" in remote:
        return "azure"
    if "gitlab" in remote:
        return "gitlab"
    return "github"


PRECOMMIT_BLOCK = """
  # Added by Plumbline — quality gate and (optionally) AI provenance trailer. See plumbline.toml.
  - repo: local
    hooks:
      - id: plumbline-gate
        name: plumbline gate (staged changes)
        entry: python3 .plumbline/plumbline.py --staged
        language: system
        pass_filenames: false
        always_run: true
        verbose: true   # show warnings even when the gate passes (warn mode is useless if nobody sees them)
      - id: plumbline-provenance
        name: plumbline AI provenance trailer
        entry: python3 .plumbline/plumbline.py --commit-msg
        language: system
        stages: [commit-msg]
"""


def merge_precommit(cfg: Path, strict: bool, dry_run: bool) -> list[tuple[str, str]]:
    """Add Plumbline as local hooks to an existing pre-commit config, without touching the team's hooks."""
    text = cfg.read_text()
    if "plumbline-gate" in text:
        return [("skip (present)", ".pre-commit-config.yaml Plumbline hooks")]
    block = PRECOMMIT_BLOCK
    if not strict:  # the trailer hook only matters when provenance trailers are required
        block = block.split("      - id: plumbline-provenance")[0]
    top_level = [l for l in text.splitlines() if l and not l[0].isspace() and not l.startswith("#")]
    if not top_level or not top_level[-1].startswith("repos:"):
        return [("todo", "could not safely append to .pre-commit-config.yaml (repos: is not its last key); "
                         "add these hooks yourself:" + block)]
    if not dry_run:
        cfg.write_text(text.rstrip("\n") + "\n" + block)
    return [("merge", ".pre-commit-config.yaml (Plumbline gate as a local hook; the team's hooks unchanged)")]


def copy_skill(dest: Path) -> None:
    """Install the /plumbline skill into dest (e.g. <repo>/.claude/skills/plumbline)."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SKILL_DIR, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="plumbline init", description="Scaffold Plumbline into a repository")
    ap.add_argument("--target", default=".")
    ap.add_argument("--ci", choices=["auto", "github", "azure", "gitlab", "none"], default="auto")
    ap.add_argument("--strict", action="store_true", help="require AI provenance commit trailers")
    ap.add_argument("--baseline", action="store_true", help="baseline existing findings (brownfield repos)")
    ap.add_argument("--no-git-hooks", action="store_true")
    ap.add_argument("--hooks", choices=["auto", "lefthook", "githooks", "pre-commit"], default="auto",
                    help="git hook manager. auto: keep the pre-commit framework if the repo uses it, else Lefthook if "
                         "available, else plain .githooks")
    ap.add_argument("--no-governance", action="store_true",
                    help="skip ARCHITECTURE/AGENTS/AI_POLICY/CONTRIBUTING/CODE_OF_CONDUCT, ADRs, AI review, rulesets")
    ap.add_argument("--no-skill", action="store_true",
                    help="don't vendor the /plumbline skill into .claude/skills (teammates then install it themselves)")
    ap.add_argument("--clients", default="all",
                    help="coding agents to set up /plumbline for: all (default), or a comma list of "
                         "claude, copilot, gemini, antigravity")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    root = Path(a.target).resolve()
    ci = detect_ci(root) if a.ci == "auto" else a.ci
    branch = default_branch(root)
    log: list[tuple[str, str]] = []

    def put(src: Path, dest_rel: str, transform=None, mode=None):
        dest = root / dest_rel
        if dest.exists() and not a.force:
            log.append(("skip (exists)", dest_rel))
            return
        log.append(("create" if not dest.exists() else "overwrite", dest_rel))
        if a.dry_run:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text().replace("__DEFAULT_BRANCH__", branch)
        dest.write_text(transform(text) if transform else text)
        if mode:
            dest.chmod(mode)

    # 1. vendored gate (pinned copy so CI never depends on the plugin being installed)
    gate = root / ".plumbline/plumbline.py"
    log.append(("update" if gate.exists() else "create", ".plumbline/plumbline.py + guard.py"))
    if not a.dry_run:
        gate.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "gate.py", gate)
        shutil.copy2(HERE / "guard.py", gate.parent / "guard.py")

    # 2. policy + contributor standard
    put(TPL / "plumbline.toml", "plumbline.toml",
        lambda t: t.replace("__REQUIRE_TRAILER__", "true" if a.strict else "false"))
    if a.no_governance:  # governance pack supersedes it with AI_POLICY.md + CONTRIBUTING.md
        put(TPL / "AI_CONTRIBUTING.md", "AI_CONTRIBUTING.md")

    # 3. CI
    if ci == "github":
        put(TPL / ".github/workflows/plumbline.yml", ".github/workflows/plumbline.yml")
        put(TPL / ".github/pull_request_template.md", ".github/pull_request_template.md")
    elif ci == "azure":
        put(TPL / "pipelines/plumbline.azure-pipelines.yml", "pipelines/plumbline.azure-pipelines.yml")
        put(TPL / ".github/pull_request_template.md", ".azuredevops/pull_request_template.md")
    elif ci == "gitlab":
        put(TPL / "pipelines/plumbline.gitlab-ci.yml", "pipelines/plumbline.gitlab-ci.yml")
        put(TPL / ".github/pull_request_template.md", ".gitlab/merge_request_templates/Default.md")

    # 3b. governance pack: shared context for parallel engineers and agents
    if not a.no_governance:
        gov = TPL / "governance"
        github_only = (".github/", "scripts/protect-main.sh")
        existing_adrs = [p for d in ("docs/adr", "docs/adrs", "docs/decisions", "adr", "doc/adr")
                         for p in (root / d).glob("[0-9][0-9][0-9][0-9]-*.md") if not p.name.startswith("0000-")]
        protection_scripts = [p.relative_to(root).as_posix() for p in (root / "scripts").glob("*")
                              if p.is_file() and p.suffix in {".sh", ".py", ".ps1"}
                              and re.search(r"rulesets|branches/[^ ]*/protection|required_status_checks",
                                            p.read_text(errors="ignore"))] if (root / "scripts").is_dir() else []
        for src in sorted(p for p in gov.rglob("*") if p.is_file()):
            rel = src.relative_to(gov).as_posix()
            if protection_scripts and rel in {".github/rulesets/main-protection.json", "scripts/protect-main.sh"}:
                log.append(("skip (repo protects its branches already)",
                            f"{rel} — keep {', '.join(protection_scripts)} as the source of truth; add the "
                            "plumbline-gate check and the human-review settings there"))
                continue
            if ci != "github" and rel.startswith(github_only):
                continue
            if rel.startswith("docs/adr/0001-") and existing_adrs:
                log.append(("skip (repo already has ADRs)", f"{rel} — {len(existing_adrs)} existing decision record(s) kept"))
                continue
            put(src, rel, mode=0o755 if src.suffix == ".sh" else None)
        if ci == "github" and not (root / ".github/CODEOWNERS").exists():
            log.append(("generate", ".github/CODEOWNERS (from ARCHITECTURE.md)"))
            if not a.dry_run:
                subprocess.run([sys.executable, str(root / ".plumbline/plumbline.py"), "--root", str(root),
                                "--codeowners", ".github/CODEOWNERS"], check=False, capture_output=True)

    # 4. git hooks — respect an existing manager; otherwise Lefthook generated from the stack, or plain .githooks
    precommit_cfg = root / ".pre-commit-config.yaml"
    if a.hooks == "auto":
        manager = "pre-commit" if precommit_cfg.exists() else ("lefthook" if wants_lefthook(root) else "githooks")
    else:
        manager = a.hooks
    if manager in {"lefthook", "githooks"} and precommit_cfg.exists() and not a.force:
        log.append(("todo", f"this repo uses the pre-commit framework; not replacing its hooks with {manager} "
                            "(pass --force to switch). Added Plumbline to .pre-commit-config.yaml instead."))
        manager = "pre-commit"
    if not a.no_git_hooks and manager == "pre-commit":
        log.extend(merge_precommit(precommit_cfg, a.strict, a.dry_run))
    elif not a.no_git_hooks and manager == "lefthook":
        existing = next((n for n in ("lefthook.yml", ".lefthook.yml", "lefthook.yaml") if (root / n).exists()), None)
        if existing and not a.force:
            log.append(("skip (exists)", f"{existing} — merge Plumbline jobs with `plumbline hooks`"))
        else:
            log.append(("create", "lefthook.yml (generated from detected stack)"))
            if is_typescript_repo(root):
                log.extend(install_ts_hooks(root, branch, a.dry_run))
            if not a.dry_run:
                (root / "lefthook.yml").write_text(lefthook_yaml(root, branch=branch))
        if not a.dry_run and (root / ".git").exists():
            ok, msg = lefthook_install(root)
            log.append(("configure" if ok else "todo", "lefthook install" if ok else msg))
    elif not a.no_git_hooks:
        put(TPL / ".githooks/pre-commit", ".githooks/pre-commit", mode=0o755)
        put(TPL / ".githooks/commit-msg", ".githooks/commit-msg", mode=0o755)
        if not a.dry_run and (root / ".git").exists():
            subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=root, check=False)
            log.append(("configure", "git core.hooksPath = .githooks"))

    # 5. Claude Code project hook (merge, don't clobber)
    settings = root / ".claude/settings.json"
    hook_cfg = json.loads((TPL / ".claude/settings.json").read_text())
    cur = json.loads(settings.read_text()) if settings.exists() else {}
    changed = False
    for event, entries in hook_cfg["hooks"].items():
        existing = cur.setdefault("hooks", {}).setdefault(event, [])
        for entry in entries:
            marker = "guard.py" if event == "PreToolUse" else "--hook"
            if not any(marker in json.dumps(h) and "plumbline" in json.dumps(h) for h in existing):
                existing.append(entry)
                changed = True
                log.append(("merge", f".claude/settings.json ({event}: "
                            f"{'human-review guard' if event == 'PreToolUse' else 'quality gate'})"))
    if changed and not a.dry_run:
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps(cur, indent=2) + "\n")
    if not changed:
        log.append(("skip (present)", ".claude/settings.json hooks"))

    # 5b. project-scoped skill: everyone who clones gets /plumbline, pinned to this version
    if not a.no_skill:
        log.append(("update" if (root / ".claude/skills/plumbline").exists() else "create",
                    ".claude/skills/plumbline/ (the /plumbline command)"))
        if not a.dry_run:
            copy_skill(root / ".claude/skills/plumbline")

    # 5c. the same /plumbline for Copilot, Gemini CLI and Antigravity (thin entry points to the shared skill)
    if not a.no_skill:
        from . import clients
        log.extend(clients.install(root, [c for c in clients.parse_clients(a.clients) if c != "claude"],
                                   SKILL_DIR / "SKILL.md", ci, a.dry_run, a.force))

    # 6. CLAUDE.md rules block (replace managed block in place)
    block = (TPL / "CLAUDE.plumbline.md").read_text()
    existing_claude = (root / "CLAUDE.md").read_text() if (root / "CLAUDE.md").exists() else ""
    if "@AGENTS.md" in existing_claude.split("<!-- plumbline:begin")[0]:
        block = block.replace("@AGENTS.md\n\n", "")
    cm = root / "CLAUDE.md"
    text = cm.read_text() if cm.exists() else "# Project instructions\n"
    if BEGIN in text:
        pre, rest = text.split(BEGIN, 1)
        post_text = rest.split(END, 1)[1] if END in rest else ""
        text = pre + block.strip() + post_text
        log.append(("refresh", "CLAUDE.md managed block"))
    else:
        text = text.rstrip() + "\n\n" + block
        log.append(("append", "CLAUDE.md managed block"))
    if not a.dry_run:
        cm.write_text(text)

    # 7. history dir + gitignore for local reports
    if not a.dry_run:
        gi = root / ".gitignore"
        lines = gi.read_text().splitlines() if gi.exists() else []
        for pat in ("plumbline.md", "plumbline*.sarif", "plumbline-full.json", "lefthook-local.yml", "__pycache__/"):
            if pat not in lines:
                lines.append(pat)
        gi.write_text("\n".join(lines) + "\n")

    # 8. brownfield baseline
    if a.baseline and not a.dry_run:
        r = subprocess.run([sys.executable, str(gate), "--all", "--write-baseline", "--root", str(root)], check=False,
                           capture_output=True, text=True)
        log.append(("baseline", (r.stdout.strip().removeprefix("plumbline: ") or ".plumbline/baseline.json")))

    print(json.dumps({"target": str(root), "ci": ci, "default_branch": branch, "strict": a.strict, "dry_run": a.dry_run,
                      "actions": [{"action": x, "path": p} for x, p in log]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
