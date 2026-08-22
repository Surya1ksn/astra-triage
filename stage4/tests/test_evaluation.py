"""
STAGE 4 TODO: validates the evaluation harness itself meets the
configured quality thresholds against the golden set. This is the same
check stage5's CI pipeline runs before allowing deployment.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation import load_golden_set, run_evaluation  # noqa: E402


def test_golden_set_loads():
    golden = load_golden_set()
    assert len(golden["cases"]) >= 8
    assert "quality_thresholds" in golden


def test_evaluation_meets_quality_thresholds():
    result = run_evaluation()
    golden = load_golden_set()
    thresholds = golden["quality_thresholds"]
    assert result.classification_accuracy >= thresholds["min_classification_accuracy"], (
        f"classification_accuracy {result.classification_accuracy} below threshold, "
        f"mismatches: {result.mismatches}"
    )
    assert result.routing_accuracy >= thresholds["min_routing_accuracy"], (
        f"routing_accuracy {result.routing_accuracy} below threshold, "
        f"mismatches: {result.mismatches}"
    )
    assert result.passed is True
