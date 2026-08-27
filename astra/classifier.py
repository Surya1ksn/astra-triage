"""
Astra Triage ticket classifier.

Ranks categories by normalized keyword overlap (hits / size of that
category's keyword set) and returns the true best-scoring category. Ties
resolve to the first-seen category in config.CATEGORIES order (an
explicit, documented tiebreak rather than an accident of iteration).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from astra import config

KEYWORDS = {
    "billing": {
        "invoice", "charge", "charged", "refund", "payment", "billing",
        "subscription", "price", "receipt", "credit", "card", "overcharged",
    },
    "technical": {
        "bug", "error", "crash", "broken", "not working", "issue",
        "exception", "failed", "failure", "500", "timeout", "slow",
    },
    "account": {
        "login", "password", "account", "locked", "reset", "signup",
        "email", "username", "access", "2fa", "verification",
    },
    "feature_request": {
        "feature", "request", "suggestion", "would be nice", "please add",
        "enhancement", "idea", "improve",
    },
    "abuse_or_security": {
        "hacked", "breach", "phishing", "abuse", "fraud", "vulnerability",
        "security", "exploit", "unauthorized", "leaked",
    },
}


@dataclass
class Classification:
    category: str
    confidence: float
    scores: dict[str, float]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def classify(subject: str, body: str) -> Classification:
    text = f"{subject}\n{body}"
    tokens = _tokenize(text)

    scores: dict[str, float] = {}
    for category in config.CATEGORIES:
        hits = len(tokens & KEYWORDS[category])
        scores[category] = hits / max(1, len(KEYWORDS[category]))

    best_category = config.CATEGORIES[0]
    best_score = -1.0
    for category in config.CATEGORIES:
        # Strict `>` so a true tie keeps the first-seen (higher-priority)
        # category instead of being overwritten by a later equal score.
        if scores[category] > best_score:
            best_score = scores[category]
            best_category = category

    return Classification(
        category=best_category,
        confidence=best_score,
        scores=scores,
    )
