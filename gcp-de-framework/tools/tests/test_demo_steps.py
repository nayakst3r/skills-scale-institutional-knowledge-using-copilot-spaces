"""Rehearses the demo playbook: each step, applied in order, must pass or fail exactly as the playbook says."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_principles as cp  # noqa: E402

REPO = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(not (REPO / "demo").exists(), reason="demo/ removed after the show")


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def commit(root, msg):
    git(root, "add", "-A")
    git(root, "-c", "user.email=demo@example.com", "-c", "user.name=demo", "commit", "-qm", msg)


def apply(root, step):
    subprocess.run([str(root / "scripts/demo-step.sh"), step], cwd=root, check=True, capture_output=True)


def rules(root, base=None):
    return {v.rule for v in cp.run(root)} | ({v.rule for v in cp.run(root, base)} if base else set())


@pytest.fixture(scope="module")
def repo(tmp_path_factory):
    root = tmp_path_factory.mktemp("demo")
    for item in ("domains", "libs", "tools", "scripts", "demo", "AGENTS.md", "ARCHITECTURE.md"):
        src = REPO / item
        (shutil.copytree if src.is_dir() else shutil.copy)(src, root / item)
    git(root, "init", "-q")
    commit(root, "iteration 0: bootstrap")
    return root


def test_steps_in_order(repo):
    apply(repo, "iteration-1-finance-domain")
    assert rules(repo, "HEAD") == set()
    commit(repo, "feat(finance): revenue in EUR")

    apply(repo, "iteration-2-guardrail-broken")
    assert rules(repo, "HEAD") == {"cross-domain-read"}
    apply(repo, "iteration-1-finance-domain")  # the fix: read sales_gold
    assert rules(repo, "HEAD") == set()

    apply(repo, "iteration-3-additive-column")
    assert rules(repo, "HEAD") == set()
    commit(repo, "feat(sales): add region to orders")

    apply(repo, "iteration-4a-breaking-broken")
    assert rules(repo, "HEAD") == {"contract-compat"}
    apply(repo, "iteration-4b-breaking-as-v2")
    assert rules(repo, "HEAD") == set()
    commit(repo, "feat(sales)!: orders_v2 with gross_amount")

    apply(repo, "iteration-5-coding-agent")
    assert rules(repo, "HEAD") == set()
    commit(repo, "feat(sales): avg_order_value on revenue_daily")

    apply(repo, "iteration-6-new-guardrail")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tools/tests/test_check_principles.py"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout
