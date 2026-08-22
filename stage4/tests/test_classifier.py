"""
STAGE 4 TODO: these tests exercise the Stage-2 classifier fix. They
should fail against the original buggy classifier.py and pass once you've
fixed the ranking + confidence normalization bugs.
"""

from astra.classifier import classify


def test_billing_ticket_classified_as_billing():
    result = classify(
        "Overcharged on my invoice",
        "I was charged twice this month, please refund the extra charge.",
    )
    assert result.category == "billing"


def test_confidence_is_normalized():
    result = classify(
        "Overcharged on my invoice",
        "I was charged twice this month, please refund the extra charge.",
    )
    assert 0.0 <= result.confidence <= 1.0


def test_true_max_wins_not_first_seen_on_strictly_higher_score():
    # "account" keywords appear twice, "billing" keywords appear once —
    # account must win even though billing is earlier in CATEGORIES.
    result = classify(
        "Login and password issue",
        "I can't log in, my password reset and account access are broken, "
        "also a small billing question.",
    )
    assert result.category == "account"


def test_empty_ticket_has_low_confidence():
    result = classify("hi", "hi")
    assert result.confidence < 0.2
