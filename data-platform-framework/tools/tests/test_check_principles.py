import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_principles as cp  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SILVER = "domains/sales/models/sales_silver_orders.sql"
GOLD = "domains/sales/models/sales_gold_revenue_daily.sql"


@pytest.fixture
def repo(tmp_path):
    """A copy of the example repo that each test can break in one specific way."""
    for d in ("domains", "libs", "macros"):
        shutil.copytree(REPO / d, tmp_path / d)
    if (REPO / "stack.yaml").exists():
        shutil.copy(REPO / "stack.yaml", tmp_path / "stack.yaml")
    return tmp_path


def edit(root, path, old, new):
    f = root / path
    text = f.read_text()
    assert old in text, f"test setup: {old!r} not in {path}"
    f.write_text(text.replace(old, new))


def rules(root):
    return {v.rule for v in cp.run(root)}


def test_example_repo_is_clean():
    assert cp.run(REPO) == []


def test_missing_contract(repo):
    (repo / "domains/sales/contracts/revenue_daily.yaml").unlink()
    assert "contract-exists" in rules(repo)


def test_bad_model_name(repo):
    (repo / GOLD).rename(repo / "domains/sales/models/revenue_daily.sql")
    assert "model-naming" in rules(repo)


def test_schema_override_in_model(repo):
    edit(repo, GOLD, "materialized='table',", "materialized='table', schema='reporting',")
    assert "model-naming" in rules(repo)


def test_cross_domain_ref_to_silver_is_blocked(repo):
    edit(repo, GOLD, "ref('sales_silver_orders')", "ref('customer_silver_customers')")
    assert "cross-domain-read" in rules(repo)


def test_cross_domain_source_of_bronze_is_blocked(repo):
    edit(repo, SILVER, "source('sales_bronze', 'raw_orders')", "source('finance_bronze', 'raw_invoices')")
    assert "cross-domain-read" in rules(repo)


def test_cross_domain_ref_to_gold_is_allowed(repo):
    edit(repo, GOLD, "ref('sales_silver_orders')", "ref('customer_gold_customers')")
    assert "cross-domain-read" not in rules(repo)


def test_direct_table_read_is_blocked(repo):
    edit(repo, GOLD, "{{ ref('sales_silver_orders') }}", "prod_catalog.sales_silver.orders")
    assert "ref-or-source" in rules(repo)


def test_cte_and_extract_are_not_table_reads(repo):
    edit(
        repo,
        GOLD,
        "    count(*) as order_count,",
        "    extract(year from order_date) as order_year,\n    count(*) as order_count,",
    )
    assert "ref-or-source" not in rules(repo)


def test_select_star_from_table(repo):
    edit(repo, GOLD, "select\n    order_date,", "select *, \n    order_date,")
    assert "no-select-star" in rules(repo)


def test_select_star_from_cte_is_fine(repo):
    (repo / GOLD).write_text(
        "{{ config(materialized='table') }}\n"
        "with final as (select order_date, currency, channel, count(*) as order_count, sum(amount) as revenue\n"
        "  from {{ ref('sales_silver_orders') }} group by order_date, currency, channel)\n"
        "select * from final\n"
    )
    assert "no-select-star" not in rules(repo)


def test_missing_data_tests(repo):
    (repo / "domains/sales/models/_sales__models.yml").write_text("version: 2\nmodels: []\n")
    assert "data-tests" in rules(repo)


def test_sql_in_orchestration(repo):
    (repo / "domains/sales/orchestration").mkdir(exist_ok=True)
    (repo / "domains/sales/orchestration/job.py").write_text('Q = "SELECT 1"\n')
    assert "orchestration-only" in rules(repo)


def test_hardcoded_credential(repo):
    (repo / "libs/de_common/oops.py").write_text('password = "hunter2hunter2"\n')
    assert "no-hardcoded-env" in rules(repo)


def test_stack_patterns_apply(repo):
    (repo / "stack.yaml").write_text(
        "stack: aws\nforbidden_literals:\n  - { pattern: 's3://', message: hard-coded bucket }\n"
    )
    edit(repo, GOLD, "group by", "-- s3://my-bucket/x\ngroup by")
    assert "no-hardcoded-env" in rules(repo)


def test_pii_without_policy_tag(repo):
    edit(repo, "domains/sales/contracts/orders.yaml", ", policy_tag: pii_email", "")
    assert "pii-policy-tag" in rules(repo)


def test_key_file_committed(repo):
    (repo / "libs/sa.pem").write_text("-----BEGIN PRIVATE KEY-----\n")
    assert "no-secrets" in rules(repo)


OLD = {
    "name": "orders",
    "version": "1.0.0",
    "columns": [
        {"name": "id", "type": "string", "mode": "REQUIRED"},
        {"name": "amount", "type": "decimal", "mode": "NULLABLE"},
    ],
}


def contract(version, columns):
    return {"name": "orders", "version": version, "columns": columns}


def test_compat_additive_nullable_with_minor_bump_ok():
    new = contract("1.1.0", OLD["columns"] + [{"name": "channel", "type": "string", "mode": "NULLABLE"}])
    assert cp.compat_violations("x", OLD, new) == []


def test_compat_dropped_column_is_breaking():
    new = contract("2.0.0", OLD["columns"][:1])
    msgs = [v.message for v in cp.compat_violations("x", OLD, new)]
    assert any("removed" in m and "orders_v2.yaml" in m for m in msgs)


def test_compat_type_change_is_breaking():
    new = contract("1.1.0", [OLD["columns"][0], {"name": "amount", "type": "string", "mode": "NULLABLE"}])
    assert any("type" in v.message for v in cp.compat_violations("x", OLD, new))


def test_compat_requires_version_bump():
    new = contract("1.0.0", OLD["columns"] + [{"name": "channel", "type": "string", "mode": "NULLABLE"}])
    assert any("not bumped" in v.message for v in cp.compat_violations("x", OLD, new))
