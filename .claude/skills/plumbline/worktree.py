"""Git worktrees for parallel work: one issue → one worktree → one branch → one PR.

Worktrees live beside the repo in `<repo>.worktrees/<branch-slug>` so several engineers' agents (or one engineer's
several agents) never share a working directory. Git hooks (Lefthook or .githooks) are shared automatically because
worktrees share the repository's hooks. Removal never touches a worktree with uncommitted or unpushed work.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import gate
from .hooks import default_branch


def git(root: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=check)


def gh_json(root: Path, *args: str):
    if not shutil.which("gh"):
        return None
    r = subprocess.run(["gh", *args], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def slugify(text: str, limit: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].rstrip("-") or "work"


def base_dir(root: Path) -> Path:
    return root.parent / f"{root.name}.worktrees"


def list_worktrees(root: Path) -> list[dict]:
    out, cur = [], {}
    for line in git(root, "worktree", "list", "--porcelain").stdout.splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
            cur = {}
            continue
        key, _, val = line.partition(" ")
        cur[key] = val or True
    main = Path(out[0]["worktree"]) if out else root
    result = []
    for w in out[1:]:
        path = Path(w["worktree"])
        branch = str(w.get("branch", "")).removeprefix("refs/heads/")
        dirty = bool(git(path, "status", "--porcelain").stdout.strip()) if path.exists() else False
        upstream = git(path, "rev-parse", "--abbrev-ref", "@{u}").stdout.strip() if path.exists() else ""
        ahead = git(path, "rev-list", "--count", f"{upstream}..HEAD").stdout.strip() if upstream else ""
        result.append({"path": str(path), "branch": branch, "dirty": dirty, "upstream": upstream or None,
                       "unpushed_commits": int(ahead) if ahead.isdigit() else None,
                       "issue": int(m.group(1)) if (m := re.match(r"\w+/(\d+)-", branch)) else None})
    return result, main


def cmd_new(root: Path, a) -> int:
    issue_title = None
    if a.issue is not None:
        data = gh_json(root, "issue", "view", str(a.issue), "--json", "title,labels,state")
        if data:
            if data.get("state") == "CLOSED":
                print(f"plumbline: issue #{a.issue} is closed.", file=sys.stderr)
                return 1
            issue_title = data["title"]
    slug = a.slug or (slugify(issue_title) if issue_title else None)
    if not slug:
        print("plumbline: give --slug (couldn't read the issue title — is `gh` installed and authenticated?)",
              file=sys.stderr)
        return 2
    branch = f"{a.type}/{a.issue}-{slug}" if a.issue is not None else f"{a.type}/{slug}"
    if git(root, "rev-parse", "--verify", "-q", f"refs/heads/{branch}").returncode == 0:
        print(f"plumbline: branch {branch} already exists — `plumbline worktree list` to find it.", file=sys.stderr)
        return 1
    db = default_branch(root)
    has_origin = bool(git(root, "remote", "get-url", "origin").stdout.strip())
    if has_origin and not a.no_fetch:
        git(root, "fetch", "--quiet", "origin", db)
    base = a.base or (f"origin/{db}" if has_origin and git(root, "rev-parse", "--verify", "-q", f"origin/{db}").returncode == 0
                      else db)
    path = base_dir(root) / branch.replace("/", "-")
    r = git(root, "worktree", "add", "--no-track", "-b", branch, str(path), base)
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
        return 1
    if a.copy_env:
        for env in (".env", ".env.local"):
            if (root / env).exists():
                shutil.copy2(root / env, path / env)
    info = {"path": str(path), "branch": branch, "base": base, "issue": a.issue, "title": issue_title}
    print(json.dumps(info, indent=2) if a.json else
          f"Worktree ready: {path}\n  branch {branch} (from {base})" + (f"\n  issue  #{a.issue}: {issue_title}" if issue_title else "")
          + f"\n  next   cd {path}")
    return 0


def cmd_list(root: Path, a) -> int:
    items, _ = list_worktrees(root)
    prs = gh_json(root, "pr", "list", "--state", "all", "--limit", "200", "--json", "number,headRefName,state,isDraft,reviewDecision") or []
    by_branch = {p["headRefName"]: p for p in prs}
    for w in items:
        pr = by_branch.get(w["branch"])
        w["pr"] = pr and {"number": pr["number"], "state": pr["state"], "draft": pr["isDraft"],
                          "review": pr.get("reviewDecision") or None}
    if a.json:
        print(json.dumps(items, indent=2))
        return 0
    if not items:
        print("No worktrees. Start one with: plumbline worktree new <issue>")
        return 0
    for w in items:
        flags = []
        if w["dirty"]:
            flags.append("uncommitted changes")
        if w["unpushed_commits"]:
            flags.append(f"{w['unpushed_commits']} unpushed")
        if w["upstream"] is None:
            flags.append("not pushed")
        pr = w["pr"]
        prs_txt = (f"PR #{pr['number']} {pr['state'].lower()}{' draft' if pr['draft'] else ''}"
                   f"{' · ' + pr['review'].lower().replace('_', ' ') if pr['review'] else ''}") if pr else "no PR"
        print(f"{w['branch']:<45} {prs_txt:<32} {', '.join(flags) or 'clean'}\n    {w['path']}")
    return 0


def _removable(root: Path, w: dict, db: str) -> tuple[bool, str]:
    if w["dirty"]:
        return False, "uncommitted changes"
    if w["unpushed_commits"]:
        return False, f"{w['unpushed_commits']} unpushed commit(s)"
    # a branch "has work" once it has moved since creation (reflog > 1 entry); a fresh branch also looks merged
    has_work = len(git(root, "reflog", "show", "--format=%H", f"refs/heads/{w['branch']}").stdout.split()) > 1
    if w.get("pr") and w["pr"]["state"] in {"MERGED", "CLOSED"}:
        return True, f"PR {w['pr']['state'].lower()}"
    if not has_work:
        return False, "no commits yet"
    merged = git(root, "branch", "--merged", f"origin/{db}" if git(root, "rev-parse", "--verify", "-q",
                                                                  f"origin/{db}").returncode == 0 else db).stdout
    if w["branch"] in [b.strip("* +") for b in merged.splitlines()]:
        return True, "merged"
    return False, "not merged"


def cmd_remove(root: Path, a) -> int:
    items, _ = list_worktrees(root)
    match = [w for w in items if (a.target.isdigit() and w["issue"] == int(a.target)) or w["branch"] == a.target
             or Path(w["path"]).name == a.target]
    if not match:
        print(f"plumbline: no worktree for '{a.target}'", file=sys.stderr)
        return 1
    w = match[0]
    if w["dirty"] or w["unpushed_commits"]:
        print(f"plumbline: refusing — {w['path']} has {'uncommitted changes' if w['dirty'] else 'unpushed commits'}. "
              "Commit and push (or discard deliberately) first.", file=sys.stderr)
        return 1
    r = git(root, "worktree", "remove", w["path"])
    print(r.stderr.strip() or f"Removed worktree {w['path']} (branch {w['branch']} kept)")
    return r.returncode


def cmd_prune(root: Path, a) -> int:
    items, _ = list_worktrees(root)
    prs = gh_json(root, "pr", "list", "--state", "all", "--limit", "200", "--json", "headRefName,state") or []
    states = {p["headRefName"]: p["state"] for p in prs}
    for w in items:
        w["pr"] = {"state": states[w["branch"]]} if w["branch"] in states else None
    db = default_branch(root)
    plan = [(w, *_removable(root, w, db)) for w in items]
    for w, ok, why in plan:
        print(f"{'remove' if ok else 'keep  '}  {w['branch']:<45} {why}")
    if not a.yes:
        print("\nDry run. Re-run with --yes to remove the worktrees marked 'remove' (branches are kept).")
        return 0
    for w, ok, _ in plan:
        if ok:
            git(root, "worktree", "remove", w["path"])
    git(root, "worktree", "prune")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="plumbline worktree", description="Isolated worktrees for parallel work")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="create a worktree + branch for an issue")
    n.add_argument("issue", nargs="?", type=int)
    n.add_argument("--slug", help="branch slug (default: from the GitHub issue title)")
    n.add_argument("--type", default="feat", choices=["feat", "fix", "chore", "docs", "refactor", "spike", "adr"])
    n.add_argument("--base", help="start point (default: origin/<default-branch>)")
    n.add_argument("--copy-env", action="store_true", help="copy .env / .env.local into the worktree")
    n.add_argument("--no-fetch", action="store_true")
    n.add_argument("--json", action="store_true")
    l = sub.add_parser("list", help="worktrees with PR and review status")
    l.add_argument("--json", action="store_true")
    r = sub.add_parser("remove", help="remove one worktree (refuses if work is uncommitted or unpushed)")
    r.add_argument("target", help="issue number, branch or folder name")
    p = sub.add_parser("prune", help="remove worktrees whose branch is merged or PR closed")
    p.add_argument("--yes", action="store_true")
    for sp in (n, l, r, p):
        sp.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    root = gate.repo_root(Path(a.root).resolve())
    common = Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip() or root / ".git")
    root = common.parent if common.name == ".git" else root  # always operate from the main checkout
    return {"new": cmd_new, "list": cmd_list, "remove": cmd_remove, "prune": cmd_prune}[a.cmd](root, a)
