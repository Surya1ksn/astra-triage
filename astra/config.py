"""
Astra Triage configuration.

STAGE 2 TODO (bug #1 — security):
    This module currently hardcodes an API key and a couple of other
    settings. That's exactly what "secure configuration and secret
    management" is testing you on. Your job:

    1. Remove the hardcoded secret below entirely (it should not exist
       in source, in git history going forward, or in any committed file).
    2. Load ASTRA_LLM_API_KEY, ASTRA_LLM_BASE_URL, ASTRA_LLM_MODEL,
       ASTRA_CLASSIFICATION_THRESHOLD, and ASTRA_RETRIEVAL_THRESHOLD from
       the environment (see .env.example — python-dotenv is already a
       dependency).
    3. The app must still work with NO .env file and NO API key set, by
       falling back to the offline stub client. Don't make the key
       required.
    4. Thresholds should be floats, validated to be within [0, 1].

    Everything below this docstring is the broken version. Fix it.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- BUG: hardcoded credential, must be removed -----------------------
LLM_API_KEY = "sk-astra-REDACTED-FAKE-VALUE"
# ------------------------------------------------------------------------

LLM_BASE_URL = os.environ.get("ASTRA_LLM_BASE_URL", "")
LLM_MODEL = "claude-sonnet-4-5"  # BUG: should also be configurable via env

# BUG: these are read as strings and never validated/converted, which will
# blow up (or silently misbehave) the first time something does
# `if score >= CLASSIFICATION_THRESHOLD`.
CLASSIFICATION_THRESHOLD = os.environ.get("ASTRA_CLASSIFICATION_THRESHOLD", "0.55")
RETRIEVAL_THRESHOLD = os.environ.get("ASTRA_RETRIEVAL_THRESHOLD", "0.30")

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
