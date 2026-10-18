"""Make /plumbline work in every coding agent the team uses, from one source of truth.

The engine and its instructions live once, in `.claude/skills/plumbline/` (an open Agent Skills folder). Each client
gets a thin entry point that points back to it, so there is nothing to keep in sync:

  claude       .claude/skills/plumbline/ (the skill itself), .claude/settings.json hooks, CLAUDE.md block
  copilot      reads Agent Skills from .claude/skills natively (VS Code, Copilot CLI, cloud agent) and AGENTS.md;
               adds .github/copilot-instructions.md, prompt files .github/prompts/plumbline-<cmd>.prompt.md
               (/plumbline-grill …) and .github/workflows/copilot-setup-steps.yml for the cloud agent
  gemini       .gemini/commands/plumbline.toml (/plumbline) and plumbline/<cmd>.toml (/plumbline:grill …);
               .gemini/settings.json reads AGENTS.md and runs the same guard and quality-gate hooks
  antigravity  .agents/skills/plumbline/SKILL.md (/plumbline in Antigravity) — a pointer to the shared skill;
               Antigravity reads AGENTS.md natively

Agent-side hooks exist for Claude Code and Gemini CLI. Every client is also covered by the git hooks, the CI gate
and the protected-branch ruleset, which do not depend on the agent at all.
"""
from __future__ import annotations

import json
from pathlib import Path

CLIENTS = ("claude", "copilot", "gemini", "antigravity")
SKILL = ".claude/skills/plumbline/SKILL.md"
RUN = "python3 .claude/skills/plumbline/run.py"

# The commands surfaced as their own entry in clients that list commands (Copilot prompts, Gemini namespaced commands).
COMMANDS = {
    "scan": ("Scan this repository: stack, modules, real imports, gaps, proposed architecture", "[path]"),
    "adopt": ("Adopt Plumbline in this existing repository, alongside the guardrails it already has", "[github|azure|gitlab]"),
    "architecture": ("Create, update, review or diagram ARCHITECTURE.md (the architecture contract)", "[create|update|review|diagram] [notes]"),
    "adr": ("Record an architecture decision (ADR) before changing the architecture", "<title>"),
    "grill": ("Grill a plan with questions, one at a time, before anything is built", "[topic]"),
    "spec": ("Write a spec (problem, stories, acceptance, out of scope) for human approval", "[title]"),
    "tickets": ("Slice an approved spec into single-module tickets in parallel waves", "<spec-issue>"),
    "feature": ("Start work on an approved issue in its own worktree and branch", "<issue>"),
    "check": ("Run the Plumbline quality gate", "[staged|all|<branch>]"),
    "fix": ("Fix the findings the quality gate reported", "[scope]"),
    "review": ("Review a branch or PR against the architecture and the review rubric (advisory)", "[branch|PR#]"),
    "rules": ("List, add, tune or disable coding rules", "[list|add|tune|disable] [change]"),
    "doctor": ("Check this repository's Plumbline setup", ""),
}

BEGIN, END = "<!-- plumbline:begin", "<!-- plumbline:end -->"


def _instructions_block() -> str:
    return (f"{BEGIN} (managed by /plumbline init — edit AGENTS.md and plumbline.toml, not this block) -->\n"
            "## Shared project context (Plumbline)\n\n"
            "Read `AGENTS.md` first and follow it. Before any code change, read `ARCHITECTURE.md` and the relevant ADRs in\n"
            "`docs/adr/`; they are binding. Only work on issues a human has labelled `ready-for-agent`.\n\n"
            f"Run the quality gate before declaring a task done: `{RUN} check --diff origin/HEAD` (or `/plumbline-check`).\n"
            "Fix findings rather than suppressing them. Never merge, approve or push to the default branch: a human code owner\n"
            "approves every pull request. End every task with the review packet described in `AGENTS.md`.\n"
            f"{END}\n")


def _merge_block(path: Path, block: str, header: str, dry: bool) -> tuple[str, str]:
    text = path.read_text() if path.exists() else header
    if BEGIN in text:
        pre, rest = text.split(BEGIN, 1)
        post = rest.split(END, 1)[1] if END in rest else ""
        new, action = pre + block.strip() + post, "refresh"
    else:
        new, action = text.rstrip() + "\n\n" + block, ("append" if path.exists() else "create")
    if path.exists() and new == path.read_text():
        return "skip (current)", path.name
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new)
    return action, path.name


def _write(root: Path, rel: str, text: str, log: list, dry: bool, force: bool, managed: bool = True) -> None:
    """Write a generated file. Generated client entry points are refreshed on every run; hand-made ones are kept."""
    dest = root / rel
    if dest.exists():
        if not managed and not force:
            log.append(("skip (exists)", rel))
            return
        if managed and "plumbline" not in dest.read_text().lower() and not force:
            log.append(("skip (exists, not Plumbline's)", rel))
            return
        if dest.read_text() == text:
            log.append(("skip (current)", rel))
            return
    log.append(("update" if dest.exists() else "create", rel))
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)


def _description(skill_md: Path) -> str:
    """The skill's description, unquoted."""
    for line in skill_md.read_text().splitlines()[1:]:
        if line.startswith("description:"):
            v = line.split(":", 1)[1].strip()
            return json.loads(v) if v.startswith('"') else v
        if line.strip() == "---":
            break
    return "Keep AI-built software true to its architecture."


# ---------------------------------------------------------------- Copilot
def copilot_prompt(cmd: str, desc: str, hint: str) -> str:
    fm = ["---", f"name: plumbline-{cmd}", f"description: {json.dumps(desc)}"]
    if hint:
        fm.append(f"argument-hint: {json.dumps(hint)}")
    fm += ["agent: agent", "---", ""]
    body = (f"Run the Plumbline `{cmd}` command.\n\n"
            f"Read [the Plumbline skill](../../{SKILL}) and follow its `{cmd}` section and the reference file it points to,\n"
            "exactly as written. The text the user typed after this prompt is the command's arguments.\n\n"
            f"Run Plumbline's engine with `{RUN} …` where the skill says to. Respect `AGENTS.md` and `ARCHITECTURE.md`.\n"
            "Never merge, approve or push to the default branch; stop and hand over with the review packet.\n")
    return "\n".join(fm) + body


COPILOT_SETUP = """# Prepares the environment the Copilot cloud agent works in, so its commits go through the same checks as people's.
# The job must be called `copilot-setup-steps`. Managed by Plumbline; edit freely, Plumbline keeps a changed file.
name: Copilot setup steps
on:
  workflow_dispatch:
  push:
    paths: [.github/workflows/copilot-setup-steps.yml]
  pull_request:
    paths: [.github/workflows/copilot-setup-steps.yml]

jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install project dependencies
        run: |
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Install git hooks (Lefthook) so the agent's commits are checked
        run: |
          if [ -f lefthook.yml ]; then npx --yes lefthook@1 install; fi
      - name: Plumbline setup check
        run: python3 .claude/skills/plumbline/run.py doctor || true
"""


def install_copilot(root: Path, skill_md: Path, ci: str, log: list, dry: bool, force: bool) -> None:
    action, _ = _merge_block(root / ".github/copilot-instructions.md", _instructions_block(),
                             "# Copilot instructions\n", dry)
    log.append((action, ".github/copilot-instructions.md (points Copilot at AGENTS.md)"))
    for cmd, (desc, hint) in COMMANDS.items():
        _write(root, f".github/prompts/plumbline-{cmd}.prompt.md", copilot_prompt(cmd, desc, hint), log, dry, force)
    if ci == "github":
        _write(root, ".github/workflows/copilot-setup-steps.yml", COPILOT_SETUP, log, dry, force, managed=False)


# ---------------------------------------------------------------- Gemini CLI
def _toml_str(s: str) -> str:
    return json.dumps(s)  # a JSON string is a valid TOML basic string


def gemini_command(cmd: str | None, desc: str) -> str:
    what = f"its `{cmd}` command" if cmd else "the command the user names"
    prompt = (f"@{{{SKILL}}}\n\n"
              f"The Plumbline skill is above. Run {what} with these arguments, following the skill and the reference file\n"
              f"it points to exactly: {{{{args}}}}\n\n"
              f"Run Plumbline's engine with `{RUN} …` where the skill says to. Respect AGENTS.md and ARCHITECTURE.md.\n"
              "Never merge, approve or push to the default branch; stop and hand over with the review packet.\n")
    return (f"# Managed by Plumbline (/plumbline init). Gemini CLI custom command.\n"
            f"description = {_toml_str(desc)}\nprompt = '''\n{prompt}'''\n")


def merge_gemini_settings(root: Path, log: list, dry: bool) -> None:
    path = root / ".gemini/settings.json"
    cur = json.loads(path.read_text()) if path.exists() else {}
    changed = False
    ctx = cur.setdefault("context", {})
    names = ctx.get("fileName", "GEMINI.md")
    names = [names] if isinstance(names, str) else list(names)
    if "AGENTS.md" not in names:
        ctx["fileName"] = ["AGENTS.md", *[n for n in names if n != "AGENTS.md"]]
        if "GEMINI.md" not in ctx["fileName"]:
            ctx["fileName"].append("GEMINI.md")
        changed = True
        log.append(("merge", ".gemini/settings.json (context: read AGENTS.md)"))
    hooks = cur.setdefault("hooks", {})
    wanted = {
        "BeforeTool": ("run_shell_command", "plumbline-human-review-guard",
                       'python3 "$GEMINI_PROJECT_DIR/.plumbline/guard.py"', 15000, "human-review guard"),
        "AfterTool": ("write_file|replace", "plumbline-quality-gate",
                      'python3 "$GEMINI_PROJECT_DIR/.plumbline/plumbline.py" --hook', 30000, "quality gate"),
    }
    for event, (matcher, name, command, timeout, label) in wanted.items():
        entries = hooks.setdefault(event, [])
        if any(name in json.dumps(e) for e in entries):
            continue
        entries.append({"matcher": matcher, "hooks": [{"type": "command", "name": name, "command": command,
                                                       "timeout": timeout}]})
        changed = True
        log.append(("merge", f".gemini/settings.json ({event}: {label})"))
    if not changed:
        log.append(("skip (present)", ".gemini/settings.json"))
    elif not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cur, indent=2) + "\n")


def install_gemini(root: Path, skill_md: Path, log: list, dry: bool, force: bool) -> None:
    _write(root, ".gemini/commands/plumbline.toml", gemini_command(None, _description(skill_md)), log, dry, force)
    for cmd, (desc, _) in COMMANDS.items():
        _write(root, f".gemini/commands/plumbline/{cmd}.toml", gemini_command(cmd, desc), log, dry, force)
    merge_gemini_settings(root, log, dry)


# ---------------------------------------------------------------- Antigravity
def antigravity_skill(skill_md: Path) -> str:
    return ("---\nname: plumbline\n"
            f"description: {json.dumps(_description(skill_md), ensure_ascii=False)}\n---\n\n"
            "# /plumbline (Antigravity entry point)\n\n"
            "Managed by Plumbline. The full skill and its engine are vendored once in `.claude/skills/plumbline/`, shared by\n"
            "every agent this team uses (Antigravity, Claude Code, Copilot, Gemini CLI).\n\n"
            f"1. Read `{SKILL}` and follow it exactly, including the reference file it names for the command.\n"
            f"2. Run Plumbline's engine with `{RUN} <command> …` (for example `{RUN} check --staged`).\n"
            "3. `AGENTS.md` and `ARCHITECTURE.md` are binding. Never merge, approve or push to the default branch; stop and\n"
            "   hand over with the review packet.\n")


def install_antigravity(root: Path, skill_md: Path, log: list, dry: bool, force: bool) -> None:
    _write(root, ".agents/skills/plumbline/SKILL.md", antigravity_skill(skill_md), log, dry, force)


def parse_clients(value: str) -> list[str]:
    if value in {"all", "auto"}:
        return list(CLIENTS)
    out = [c.strip() for c in value.split(",") if c.strip()]
    bad = [c for c in out if c not in CLIENTS]
    if bad:
        raise SystemExit(f"plumbline: unknown client(s) {', '.join(bad)} — choose from {', '.join(CLIENTS)} or all")
    return out


def install(root: Path, clients: list[str], skill_md: Path, ci: str, dry: bool, force: bool) -> list:
    log: list = []
    if "copilot" in clients:
        install_copilot(root, skill_md, ci, log, dry, force)
    if "gemini" in clients:
        install_gemini(root, skill_md, log, dry, force)
    if "antigravity" in clients:
        install_antigravity(root, skill_md, log, dry, force)
    return log


def main(argv: list[str]) -> int:
    """plumbline clients [--root .] [--clients all|copilot,gemini,antigravity] [--dry-run] [--force]"""
    import argparse
    from . import gate
    ap = argparse.ArgumentParser(prog="plumbline clients",
                                 description="Add /plumbline entry points for Copilot, Gemini CLI and Antigravity")
    ap.add_argument("--root", default=".")
    ap.add_argument("--clients", default="all", help="all, or a comma list of " + ", ".join(CLIENTS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    root = gate.repo_root(Path(a.root).resolve())
    skill_md = root / SKILL
    if not skill_md.exists():
        print(f"plumbline: {SKILL} is missing — run `plumbline init` first", flush=True)
        return 1
    ci = "github" if (root / ".github").is_dir() else "other"
    log = install(root, parse_clients(a.clients), skill_md, ci, a.dry_run, a.force)
    for action, what in log:
        print(f"{action:<8} {what}")
    return 0
