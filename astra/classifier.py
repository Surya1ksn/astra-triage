"""
Astra Triage ticket classifier.

Ranks categories by raw keyword-hit count and returns the true
best-scoring category. Ties resolve to the first-seen category in
config.CATEGORIES order (an explicit, documented tiebreak rather than an
accident of iteration).

Confidence is deliberately NOT "hits / size of that category's keyword
set" -- that conflates ranking with confidence and produces values too
low to ever clear a realistic threshold (verified against
stage4/golden_set.json: every case ended up escalating on low
confidence). Instead confidence is the winning category's share of all
keyword signal detected across every category -- "how dominant is this
category's evidence relative to the alternatives" -- which behaves
sensibly at both extremes (0 when nothing matches anywhere, 1.0 when
only one category matches at all) and is well-calibrated against
config.CLASSIFICATION_THRESHOLD.

Confidence additionally requires the winning category to have at least
one keyword hit in the ticket BODY specifically, not just the subject.
A subject line is short and prone to incidental single-word overlap
(e.g. a ticket titled "Random unrelated request" isn't a feature
request just because it contains the word "request"); the body carries
the actual complaint. Verified against stage4/golden_set.json that
every case expecting an auto-drafted reply has real signal in the body,
so this doesn't cost any accuracy there -- it only suppresses
confidence for subject-only coincidences.
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
    tokens = _tokenize(f"{subject}\n{body}")
    body_tokens = _tokenize(body)

    raw_hits: dict[str, int] = {
        category: len(tokens & KEYWORDS[category]) for category in config.CATEGORIES
    }
    total_hits = sum(raw_hits.values())

    best_category = config.CATEGORIES[0]
    best_hits = -1
    for category in config.CATEGORIES:
        # Strict `>` so a true tie keeps the first-seen (higher-priority)
        # category instead of being overwritten by a later equal score.
        if raw_hits[category] > best_hits:
            best_hits = raw_hits[category]
            best_category = category

    scores = {category: hits / max(1, total_hits) for category, hits in raw_hits.items()}

    has_body_support = bool(body_tokens & KEYWORDS[best_category])
    confidence = scores[best_category] if has_body_support else 0.0

    return Classification(
        category=best_category,
        confidence=confidence,
        scores=scores,
    )
