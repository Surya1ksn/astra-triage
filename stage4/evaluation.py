"""
Astra Triage golden-set evaluation.

Runs every case in golden_set.json through astra.graph.run_ticket and
scores classification_accuracy and routing_accuracy against the
configured quality_thresholds. Used both as a library (stage4/tests,
stage5's CI evaluate job) and as a script (`python stage4/evaluation.py`,
exits non-zero on failure to gate deployment).

Explicitly adds the repo root to sys.path before importing astra: running
this file directly (`python stage4/evaluation.py`, the invocation this
module's own script mode is meant to support) only puts this file's own
directory on sys.path, not the repo root, so `import astra` would
otherwise fail outside of pytest (which adds the repo root itself via
pyproject.toml's pythonpath setting).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from astra.graph import run_ticket  # noqa: E402
from astra.retrieval import KnowledgeBase  # noqa: E402

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"


@dataclass
class EvaluationResult:
    classification_accuracy: float
    routing_accuracy: float
    passed: bool
    mismatches: list[dict]


def load_golden_set() -> dict:
    with open(GOLDEN_SET_PATH) as f:
        return json.load(f)


def run_evaluation() -> EvaluationResult:
    golden = load_golden_set()
    thresholds = golden["quality_thresholds"]
    knowledge_base = KnowledgeBase()

    correct_classification = 0
    correct_routing = 0
    mismatches: list[dict] = []

    for case in golden["cases"]:
        state = run_ticket(case["subject"], case["body"], knowledge_base=knowledge_base)
        actual_category = state.classification.category if state.classification else None
        actual_outcome = "escalate" if state.escalated else "draft"

        classification_ok = actual_category == case["expected_category"]
        routing_ok = actual_outcome == case["expected_outcome"]
        correct_classification += classification_ok
        correct_routing += routing_ok

        if not (classification_ok and routing_ok):
            mismatches.append(
                {
                    "id": case["id"],
                    "expected_category": case["expected_category"],
                    "actual_category": actual_category,
                    "expected_outcome": case["expected_outcome"],
                    "actual_outcome": actual_outcome,
                }
            )

    total = len(golden["cases"])
    classification_accuracy = correct_classification / total
    routing_accuracy = correct_routing / total
    passed = (
        classification_accuracy >= thresholds["min_classification_accuracy"]
        and routing_accuracy >= thresholds["min_routing_accuracy"]
    )

    return EvaluationResult(
        classification_accuracy=classification_accuracy,
        routing_accuracy=routing_accuracy,
        passed=passed,
        mismatches=mismatches,
    )


def main() -> None:
    result = run_evaluation()
    print(f"classification_accuracy: {result.classification_accuracy:.3f}")
    print(f"routing_accuracy: {result.routing_accuracy:.3f}")
    if result.mismatches:
        print("\nMismatches:")
        for m in result.mismatches:
            print(f"  - {m}")
    if not result.passed:
        print("\nEVALUATION FAILED: below configured quality thresholds.")
        sys.exit(1)
    print("\nEvaluation passed.")


if __name__ == "__main__":
    main()
