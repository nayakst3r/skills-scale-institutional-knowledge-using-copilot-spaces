"""Human-review guard: a Claude Code PreToolUse hook for the Bash tool.

Blocks shell commands that would let an agent skip human review: merging or approving pull requests, pushing or
committing directly to the protected branch, force-pushing, bypassing git hooks, enabling auto-merge, or editing
branch protection. Exit code 2 tells the agent the command was refused and why.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import shlex
import subprocess
import sys

PROTECTED = {"main", "master", "trunk", "develop"}

RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bgh\s+pr\s+merge\b"), "merging a pull request"),
    (re.compile(r"\bgh\s+pr\s+review\b.*(--approve|\s-a\b)"), "approving a pull request"),
    (re.compile(r"\bgh\s+pr\s+(merge|edit)\b.*--auto\b|\bgh\s+pr\s+merge\b.*--auto"), "enabling auto-merge"),
    (re.compile(r"\bgh\s+api\b.*(pulls/\d+/merge|/reviews\b.*APPROVE|event=APPROVE)"), "merging/approving via the API"),
    (re.compile(r"\bgh\s+api\b.*(rulesets|branches/[^/\s]+/protection)\b.*(-X|--method)\s*(DELETE|PUT|PATCH|POST)"),
     "changing branch protection"),
    (re.compile(r"\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+\S)"), "force-pushing"),
    (re.compile(r"\bgit\s+config\b.*core\.hooksPath\s+(?!\.githooks)"), "redirecting git hooks"),
]


def agent_ready_label() -> str | None:
    """The label that releases work to agents. Only humans may apply it (plumbline.toml: agent_ready_label)."""
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    cfg = Path(top) / "plumbline.toml" if top else None
    if not cfg or not cfg.exists():
        return None
    try:
        import tomllib
        data = tomllib.loads(cfg.read_text())
    except Exception:  # unreadable config must not disable the guard's other rules
        return "ready-for-agent"
    section = data.get("plumbline", data)
    if section.get("humans_release_work", True) is False:
        return None
    return section.get("agent_ready_label", "ready-for-agent")


def has_commits() -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], capture_output=True).returncode == 0


def current_branch() -> str:
    out = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    return out.stdout.strip()


def violations(command: str) -> list[str]:
    found = [why for rx, why in RULES if rx.search(command)]
    label = agent_ready_label() if re.search(r"\bgh\s+(issue|pr)\s+(create|edit)\b|\bgh\s+api\b.*labels", command) else None
    if label and re.search(rf"(--label|--add-label|-l|labels(\[\])?)[\s=]+[\"']?[^\"'|;&]*\b{re.escape(label)}\b", command):
        found.append(f"applying the '{label}' label (only a human releases work to agents)")
    for part in re.split(r"&&|\|\||;|\|", command):
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        if words and words[0] == "git":
            flags = [w for w in words[1:] if w.startswith("-") and not w.startswith("--") or w == "--no-verify"]
            if "--no-verify" in flags or (len(words) > 1 and words[1] == "commit" and any(
                    f.startswith("-") and not f.startswith("--") and "n" in f[1:] for f in flags)):
                found.append("bypassing git hooks")
        if len(words) >= 2 and words[0] == "git" and words[1] == "push":
            targets = [w.split(":")[-1] for w in words[2:] if not w.startswith("-")]
            if any(t in PROTECTED for t in targets) or (len(targets) <= 1 and current_branch() in PROTECTED):
                found.append("pushing directly to a protected branch")
        if len(words) >= 2 and words[0] == "git" and words[1] in {"commit", "merge", "rebase", "cherry-pick"}:
            if current_branch() in PROTECTED and words[1] != "rebase" and has_commits():
                found.append(f"running `git {words[1]}` on the protected branch '{current_branch()}'")
    return sorted(set(found))


SHELL_TOOLS = {"Bash", "run_shell_command"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    # Claude Code calls its shell tool "Bash"; Gemini CLI calls it "run_shell_command". Same payload shape otherwise.
    if payload.get("tool_name") not in SHELL_TOOLS:
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    found = violations(command)
    if not found:
        return 0
    sys.stderr.write(
        "Blocked by Plumbline human-review guard: " + "; ".join(found) + ".\n"
        "Every change reaches the protected branch only through a pull request approved by a human code owner.\n"
        "Stop here, push your feature branch, open (or update) the PR, and hand over with a review packet "
        "(see reference/human-review.md). A human must do this step themselves.\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
