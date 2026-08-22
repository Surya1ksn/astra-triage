"""
Astra Triage CLI entrypoint.

STAGE 3 TODO:
    Once astra.graph.run_ticket works, wire up a small CLI so a ticket can
    be run end-to-end from the terminal, e.g.:

        python -m astra.main --subject "Overcharged" --body "I was charged twice..."

    Print a structured result: category, confidence, whether it was
    escalated (and why), the retrieved source titles + scores, and the
    draft (if any).

    Currently this just parses args and calls the not-yet-implemented
    run_ticket, so it will raise NotImplementedError until Stage 3 is
    done — that's expected and fine as a starting point.
"""

from __future__ import annotations

import argparse
import json

from astra.graph import run_ticket


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a support ticket through Astra Triage.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    args = parser.parse_args()

    state = run_ticket(args.subject, args.body)

    result = {
        "category": state.classification.category if state.classification else None,
        "confidence": state.classification.confidence if state.classification else None,
        "escalated": state.escalated,
        "escalation_reason": state.escalation_reason,
        "retrieved_sources": [
            {"title": doc.title, "score": round(score, 3)} for doc, score in state.retrieved
        ],
        "draft": state.draft,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
