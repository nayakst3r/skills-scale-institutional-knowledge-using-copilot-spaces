import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_principles as cp  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def repo(tmp_path):
    """A copy of the example repo that each test can break in one specific way."""
    for d in ("domains", "libs"):
        shutil.copytree(REPO / d, tmp_path / d)
    return tmp_path


def rules(root):
    return {v.rule for v in cp.run(root)}


def test_example_repo_is_clean():
    assert cp.run(REPO) == []


def test_missing_contract(repo):
    (repo / "domains/sales/contracts/revenue_daily.yaml").unlink()
    assert "contract-exists" in rules(repo)


def test_cross_domain_read_of_silver_is_blocked(repo):
    f = repo / "domains/sales/transforms/gold_revenue_daily.sqlx"
    f.write_text(f.read_text().replace('ref("sales_silver", "orders")', 'ref("customer_silver", "customers")'))
    assert "cross-domain-read" in rules(repo)


def test_cross_domain_read_of_gold_is_allowed(repo):
    f = repo / "domains/sales/transforms/gold_revenue_daily.sqlx"
    f.write_text(f.read_text().replace('ref("sales_silver", "orders")', 'ref("customer_gold", "customers")'))
    assert "cross-domain-read" not in rules(repo)


def test_select_star_in_silver(repo):
    f = repo / "domains/sales/transforms/silver_orders.sqlx"
    f.write_text(f.read_text().replace("SELECT\n  order_id,", "SELECT *, \n  order_id,"))
    assert "no-select-star" in rules(repo)


def test_hardcoded_project(repo):
    f = repo / "domains/sales/transforms/gold_revenue_daily.sqlx"
    f.write_text(f.read_text().replace('${ref("sales_silver", "orders")}', "`de-prod.sales_silver.orders`"))
    assert "no-hardcoded-env" in rules(repo)


def test_sql_in_dag(repo):
    f = repo / "domains/sales/dags/sales_daily.py"
    f.write_text(f.read_text() + '\nQ = "SELECT 1"\n')
    assert "dag-orchestration-only" in rules(repo)


def test_missing_assertions(repo):
    f = repo / "domains/sales/transforms/gold_revenue_daily.sqlx"
    text = f.read_text()
    f.write_text(text.replace(text[text.index("  assertions"):text.index("}\n\nSELECT")], ""))
    assert "assertions" in rules(repo)


def test_pii_without_policy_tag(repo):
    f = repo / "domains/sales/contracts/orders.yaml"
    f.write_text(f.read_text().replace(", policy_tag: pii_email", ""))
    assert "pii-policy-tag" in rules(repo)


def test_wrong_schema_name(repo):
    f = repo / "domains/sales/transforms/silver_orders.sqlx"
    f.write_text(f.read_text().replace('"sales_silver"', '"sales_staging"'))
    assert "layer-naming" in rules(repo)


OLD = {"name": "orders", "version": "1.0.0", "columns": [
    {"name": "id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "amount", "type": "NUMERIC", "mode": "NULLABLE"},
]}


def contract(version, columns):
    return {"name": "orders", "version": version, "columns": columns}


def test_compat_additive_nullable_with_minor_bump_ok():
    new = contract("1.1.0", OLD["columns"] + [{"name": "channel", "type": "STRING", "mode": "NULLABLE"}])
    assert cp.compat_violations("x", OLD, new) == []


def test_compat_dropped_column_is_breaking():
    new = contract("2.0.0", OLD["columns"][:1])
    msgs = [v.message for v in cp.compat_violations("x", OLD, new)]
    assert any("removed" in m and "orders_v2.yaml" in m for m in msgs)


def test_compat_type_change_is_breaking():
    new = contract("1.1.0", [OLD["columns"][0], {"name": "amount", "type": "STRING", "mode": "NULLABLE"}])
    assert any("type" in v.message for v in cp.compat_violations("x", OLD, new))


def test_compat_requires_version_bump():
    new = contract("1.0.0", OLD["columns"] + [{"name": "channel", "type": "STRING", "mode": "NULLABLE"}])
    assert any("not bumped" in v.message for v in cp.compat_violations("x", OLD, new))
