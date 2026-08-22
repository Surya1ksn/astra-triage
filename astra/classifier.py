"""
Astra Triage ticket classifier.

STAGE 2 TODO (bug #2 — ranking logic):
    `classify()` is supposed to return the category with the HIGHEST
    keyword-overlap score, plus a confidence in [0, 1]. As written it has
    at least two bugs:

    1. It iterates categories in a way that keeps the *first* category
       whose score is merely >= the running best, using the wrong
       comparison operator — so ties (and the deliberately-ordered
       CATEGORIES list) silently favor whichever category happens to come
       first, not the true best match.
    2. Confidence is computed as raw keyword hits without normalizing by
       ticket length or keyword-set size, so a long ticket that happens to
       mention one billing word gets an inflated "confident" score, and a
       short precise ticket gets an artificially low one.

    Fix the ranking so it genuinely returns the best-scoring category, and
    fix the confidence calculation so it's a normalized value in [0, 1]
    that behaves sensibly (e.g. Jaccard-style overlap, or hits / max(1,
    len(keywords))). Add/adjust unit tests in stage4/tests to lock in the
    corrected behavior.
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
        scores[category] = float(hits)  # BUG: not normalized

    best_category = config.CATEGORIES[0]
    best_score = -1.0
    for category in config.CATEGORIES:
        # BUG: `>=` means later categories with an EQUAL score overwrite
        # earlier, higher-priority ones, and ties aren't resolved by any
        # real tiebreak rule (should be first-seen-wins on true ties, or
        # an explicit documented tiebreak).
        if scores[category] >= best_score:
            best_score = scores[category]
            best_category = category

    return Classification(
        category=best_category,
        confidence=best_score,  # BUG: raw hit count, not a [0,1] confidence
        scores=scores,
    )
