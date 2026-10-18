"""Runtime settings, read once from environment variables (ARCHITECTURE.md section 7)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    landing_dir: Path
    dbt_target: str


def load() -> Settings:
    """Read settings from the environment, with defaults that work on a laptop and in CI."""
    return Settings(
        landing_dir=Path(os.environ.get("KESTREL_LANDING_DIR", "landing")),
        dbt_target=os.environ.get("KESTREL_DBT_TARGET", "local"),
    )
