#!/usr/bin/env python3
"""Run the Plumbline CLI straight from this skill folder — no install needed (stdlib Python 3.11+).

The folder is itself the `plumbline` package, loaded by path so it works whatever the folder is named.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("plumbline", HERE / "__init__.py",
                                              submodule_search_locations=[str(HERE)])
pkg = importlib.util.module_from_spec(spec)
sys.modules["plumbline"] = pkg
spec.loader.exec_module(pkg)

from plumbline.cli import main  # noqa: E402

sys.exit(main())
