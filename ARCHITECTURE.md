# Architecture

> The shared source of truth for every engineer and every AI agent working on this repository.
> Changing this file after the first merge requires an ADR in `docs/adr/` (rule PL015).

## 1. Purpose
Kestrel Energy (fictional) is an Australian electricity retailer. This platform turns smart-meter readings, delivered
as NEM12 files, into trusted daily usage per meter and daily charges per customer account. Success means every
customer's bill is built from complete, validated readings, and downstream teams read only published (gold) tables.

## 2. Context
- **Sources:** NEM12 interval-data files from metering data providers (one file per provider per day).
- **Reference data:** customer accounts and tariffs from the CRM, delivered as a daily extract.
- **Consumers:** billing (daily charges), the customer app (usage charts), finance reporting. All read `*_gold_*` only.
- **Orchestration:** Airflow schedules ingestion and `dbt build` once a day.

## 3. Quality attributes (ranked)
1. **Correctness:** no reading is lost or double-counted; usage per day reconciles to the source files.
2. **Traceability:** every gold row can be traced back to its source file and NEM12 record.
3. **Freshness:** yesterday's usage is published by 07:00 AEST.

## 4. Constraints
- Customer and meter data stays in Australia (Privacy Act; AEMO data rules).
- NEM12 interval timestamps are in market time (AEST, UTC+10, no daylight saving). Store and compare in market time.
- No credentials in code or config files. Connection settings come from environment variables.

## 5. Tech stack
- Python 3.12 for ingestion (standard library only for parsing)
- dbt Core 1.12 with DuckDB locally and in CI (`dbt-duckdb`)
- Apache Airflow for scheduling (provided by the managed runtime)
- GitHub Actions for CI

Agents must not add alternatives to any of these (no pandas, Spark or a second transformation tool).

## 6. Modules and boundaries
Each module owns one responsibility. A module may depend only on the modules in its `may_import` list.
The block below is enforced on every file an agent writes, on every commit and on every pull request. For dbt models,
`ref()` counts as an import.

| Module | Responsibility | Owners |
|---|---|---|
| ingestion | Parse and validate NEM12 files into landing tables. Pure parsing, no warehouse access. | Metering pod |
| shared | Configuration and small helpers used by ingestion and orchestration. | Platform pod |
| orchestration | Airflow DAGs. Schedule only: no SQL, no data logic, no dataframes. | Platform pod |
| metering | dbt models for interval reads: bronze → silver → gold daily usage. | Metering pod |
| customer | dbt models for accounts and tariffs. Holds personal data (PII). | Customer pod |
| billing | dbt models that price usage into daily charges. Reads metering and customer **gold** only. | Billing pod |

```toml plumbline-architecture
source_roots = ["src", "dags", "models"]
strict_placement = true          # new code must live inside a declared module
architecture_owners = ["@nayakst3r"]   # review shared context: this file, AGENTS.md, policies, CI

[[module]]
name = "ingestion"
paths = ["src/kestrel/ingestion/**"]
may_import = ["shared"]
forbid_packages = ["dbt", "airflow", "pandas", "polars", "pyspark", "requests", "boto3"]
owners = ["@nayakst3r"]

[[module]]
name = "shared"
paths = ["src/kestrel/shared/**", "src/kestrel/__init__.py"]
may_import = []
forbid_packages = ["pandas", "polars", "pyspark", "requests"]
owners = ["@nayakst3r"]

[[module]]
name = "orchestration"
paths = ["dags/**"]
may_import = ["shared"]
forbid_packages = ["pandas", "polars", "pyspark", "duckdb", "sqlalchemy", "requests"]
owners = ["@nayakst3r"]

[[module]]
name = "metering"
paths = ["models/metering/**"]
may_import = []
owners = ["@nayakst3r"]

[[module]]
name = "customer"
paths = ["models/customer/**"]
may_import = []
owners = ["@nayakst3r"]

[[module]]
name = "billing"
paths = ["models/billing/**"]
may_import = ["metering", "customer"]
owners = ["@nayakst3r"]
```

> In a real engagement each pod is its own GitHub team (for example `@kestrel/metering`). This demo repository
> uses one account for every owner.

## 7. Cross-cutting conventions
- **Layers and names:** models are `<domain>_<bronze|silver|gold>_<table>`. Bronze is raw and append-only, silver is
  typed and de-duplicated, gold is the published interface.
- **Cross-domain reads:** a domain reads another domain's **gold** models only, through `ref()`.
- **Data tests:** every silver and gold model has `not_null` and `unique` (or a unique combination) on its key.
- **Energy and money:** energy in kWh as `decimal(18,3)`; money in AUD as `decimal(18,2)`, GST shown separately.
- **Time:** interval and reading dates are market time (AEST). Never convert to local daylight-saving time.
- **Personal data:** only the `customer` domain holds PII, tagged `meta: {pii: true}` in its schema file.
- **Errors:** ingestion rejects a malformed file as a whole with a typed error. Never skip bad rows silently.
- **Configuration:** environment variables only, read once in `shared`.

## 8. Key decisions
See [docs/adr](docs/adr/). The most recent accepted ADR wins over anything in this file it contradicts, and this
file is updated in the same PR.
