"""Rehearses the demo playbook on every stack: each step, applied in order, must pass or fail exactly as
the playbook says. When dbt is installed, every passing step is also built and tested on DuckDB."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_principles as cp  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
STACKS = sorted(p.name for p in (REPO / "stacks").iterdir() if (p / "stack.yaml").exists())
HAS_DBT = (
    shutil.which("dbt") is not None
    and subprocess.run(["dbt", "--version"], capture_output=True).stdout.find(b"duckdb") >= 0
)

pytestmark = pytest.mark.skipif(not (REPO / "demo").exists(), reason="demo/ removed after the show")


def sh(root, *args):
    return subprocess.run(args, cwd=root, check=True, capture_output=True, text=True)


def commit(root, msg):
    sh(root, "git", "add", "-A")
    sh(root, "git", "-c", "user.email=demo@example.com", "-c", "user.name=demo", "commit", "-qm", msg)


def rules(root):
    return {v.rule for v in cp.run(root)} | {v.rule for v in cp.run(root, "HEAD")}


def local_build(root):
    if HAS_DBT:
        r = subprocess.run(["make", "-s", "local-build"], cwd=root, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout[-3000:]


def make_repo(tmp_path, stack):
    root = tmp_path / stack
    skip = shutil.ignore_patterns(".git", "target", "__pycache__", ".pytest_cache")

    def ignore(folder, names):  # start from the stack-neutral template, even if this repo already chose a stack
        top = {"stack.yaml", ".stack-files"} if Path(folder) == REPO else set()
        return set(skip(folder, names)) | (top & set(names))

    shutil.copytree(REPO, root, ignore=ignore)
    sh(root, "git", "init", "-q")
    sh(root, "./scripts/use-stack.sh", stack, "--force")
    commit(root, f"step 0: bootstrap on {stack}")
    return root


@pytest.mark.parametrize("stack", STACKS)
def test_demo_steps_in_order(tmp_path, stack):
    repo = make_repo(tmp_path, stack)
    step = lambda name: sh(repo, "./scripts/demo-step.sh", name)  # noqa: E731

    step("iteration-1-finance-domain")
    assert rules(repo) == set()
    orchestration = list((repo / "domains/finance/orchestration").iterdir())
    assert len(orchestration) == 1, f"{stack}: expected one finance orchestration file"
    if stack == STACKS[0]:
        local_build(repo)  # dbt SQL is identical on every stack: building it once is enough
    commit(repo, "feat(finance): revenue in EUR")

    step("iteration-2-guardrail-broken")
    assert rules(repo) == {"cross-domain-read"}
    step("iteration-1-finance-domain")  # the fix: read sales gold
    assert rules(repo) == set()

    step("iteration-3-additive-column")
    assert rules(repo) == set()
    if stack == STACKS[0]:
        local_build(repo)
    commit(repo, "feat(sales): add region to orders")

    step("iteration-4a-breaking-broken")
    assert rules(repo) == {"contract-compat"}
    step("iteration-4b-breaking-as-v2")
    assert rules(repo) == set()
    if stack == STACKS[0]:
        local_build(repo)
    commit(repo, "feat(sales)!: orders_v2 with gross_amount")

    step("iteration-5-coding-agent")
    assert rules(repo) == set()
    if stack == STACKS[0]:
        local_build(repo)
    commit(repo, "feat(sales): avg_order_value on revenue_daily")

    step("iteration-6-new-guardrail")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tools/tests/test_check_principles.py"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout
    assert "idempotent-incremental" in (repo / "tools/check_principles.py").read_text()
