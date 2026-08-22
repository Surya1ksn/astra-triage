"""
Astra Triage golden-set evaluation.

STAGE 4 TODO:
    Complete `run_evaluation()` so it:

    1. Loads stage4/golden_set.json.
    2. Runs every case through astra.graph.run_ticket (Stage 3 must be
       done first).
    3. Computes:
       - classification_accuracy: fraction of cases where
         state.classification.category == case["expected_category"].
       - routing_accuracy: fraction of cases where the actual outcome
         ("escalate" if state.escalated else "draft") matches
         case["expected_outcome"].
    4. Compares both against golden_set["quality_thresholds"], and
       returns/raises a clear pass/fail result plus a per-case breakdown
       of mismatches (id, expected vs actual) for debugging.
    5. Is runnable both as a library function (used by stage4/tests and
       by stage5's CI pipeline) and as a script:

           python stage4/evaluation.py

       which should print a summary and exit non-zero if either threshold
       isn't met (this is what stage5/pipeline.yml gates deployment on).

    Currently this is a stub that raises NotImplementedError.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

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
    """TODO: implement per the module docstring."""
    raise NotImplementedError("Implement golden-set evaluation (Stage 4).")


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
