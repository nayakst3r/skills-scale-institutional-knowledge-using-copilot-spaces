"""Environment config (P6). Code never hard-codes projects, buckets or envs; it asks here."""

import os


def env() -> str:
    return os.environ["DE_ENV"]  # dev | stg | prod, set on the Composer environment


def project_id() -> str:
    return os.environ["DE_PROJECT_ID"]


def region() -> str:
    return os.environ.get("DE_REGION", "europe-west2")


def dataform_repo() -> str:
    return os.environ.get("DE_DATAFORM_REPO", "de-platform")
