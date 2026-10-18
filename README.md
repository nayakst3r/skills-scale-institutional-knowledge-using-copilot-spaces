# Kestrel Energy — meter data platform

> **Fictional example.** Kestrel Energy is an invented Australian electricity retailer, used to demonstrate
> [Plumbline](https://github.com/OWNER/plumbline) on a data engineering project. All data here is synthetic.

Kestrel receives smart-meter readings from metering providers as **NEM12** files (the Australian Energy Market
Operator's interval-data format). This repository turns them into trusted daily usage and billing tables.

```
NEM12 files ──► ingestion (Python) ──► landing/ ──► dbt: metering_bronze ─► metering_silver ─► metering_gold
                                                                                   │
                                   customer_* (accounts) ─────────────────────────┤
                                                                                   ▼
                                                                         billing_gold_daily_charges
Airflow schedules it (orchestration only: no data logic in DAGs).
```

## Run it locally (DuckDB, no cloud needed)
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
make ingest     # parse sample NEM12 → landing/
make build      # dbt build: models + data tests on DuckDB
make test       # Python unit tests
make check      # Plumbline quality gate
```

Read `ARCHITECTURE.md` and `AGENTS.md` before changing anything.
