"""Environment config (P6). Code never hard-codes projects, catalogs, buckets or envs; it asks here.

Every setting is an environment variable named DE_<NAME>, set on the orchestrator (Composer, MWAA,
Airflow, Fabric) or the CI environment, never in code.
"""

import os


def setting(name: str, default: str | None = None) -> str:
    value = os.environ.get(f"DE_{name.upper()}", default)
    if value is None:
        raise KeyError(f"missing environment variable DE_{name.upper()}")
    return value


def env() -> str:
    return setting("env")  # local | dev | stg | prod
