"""
Astra Triage configuration.

Secrets are read from the environment only (ASTRA_LLM_API_KEY) — never
hardcoded and never required. With no .env and no key set, the app runs
fully offline via the llm_client stub. Thresholds are read from env,
converted to float, and validated to be within [0, 1] at import time so
misconfiguration fails loudly instead of silently comparing str >= float
downstream.
"""

import os

from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.environ.get("ASTRA_LLM_API_KEY") or None
LLM_BASE_URL = os.environ.get("ASTRA_LLM_BASE_URL", "")
LLM_MODEL = os.environ.get("ASTRA_LLM_MODEL", "claude-sonnet-4-5")


def _get_threshold(env_var: str, default: float) -> float:
    raw = os.environ.get(env_var)
    if raw is None:
        value = default
    else:
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{env_var}={raw!r} is not a valid float") from exc
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{env_var}={value!r} must be within [0, 1]")
    return value


CLASSIFICATION_THRESHOLD = _get_threshold("ASTRA_CLASSIFICATION_THRESHOLD", 0.55)
# 0.25, not the originally-suggested 0.30: measured against
# stage4/golden_set.json with the offline TF-IDF retriever, 0.30 missed a
# real relevant match (0.281 similarity) on a legitimate billing query.
RETRIEVAL_THRESHOLD = _get_threshold("ASTRA_RETRIEVAL_THRESHOLD", 0.25)

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base")

CATEGORIES = [
    "billing",
    "technical",
    "account",
    "feature_request",
    "abuse_or_security",
]

# Categories that must always be escalated to a human regardless of
# classification confidence or retrieval quality.
ALWAYS_ESCALATE_CATEGORIES = {"abuse_or_security"}
