"""
Astra Triage LangGraph orchestration.

STAGE 3 TODO:
    Build the actual state graph described in stage1/diagrams/pipeline.md
    and stage3/NOTES.md using LangGraph. Currently `build_graph()` and
    `run_ticket()` are stubs.

    Expected shape:

      TriageState (TypedDict or pydantic model) should carry at least:
        subject, body, classification, retrieved, draft, escalated,
        escalation_reason

      Nodes:
        - classify_node: runs astra.classifier.classify, writes
          `classification` into state.
        - retrieve_node: runs KnowledgeBase().search_relevant() using the
          ticket text as the query, writes `retrieved` into state.
        - draft_node: runs astra.draft.draft_response, writes `draft`.
        - escalate_node: sets `escalated = True` and a human-readable
          `escalation_reason`.

      Conditional routing (implement as a LangGraph conditional edge
      function, not buried inside a node):
        - after classify_node: if classification.category in
          config.ALWAYS_ESCALATE_CATEGORIES, or confidence below
          config.CLASSIFICATION_THRESHOLD -> escalate_node.
          Otherwise -> retrieve_node.
        - after retrieve_node: if `retrieved` is empty -> escalate_node.
          Otherwise -> draft_node.
        - draft_node and escalate_node both terminate the graph.

    Keep node functions small and testable independent of LangGraph
    itself where reasonable (e.g. a pure `_decide_after_classify(state)
    -> str` helper you can unit test directly, that the LangGraph
    conditional edge just calls).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from astra import config
from astra.classifier import Classification, classify
from astra.draft import draft_response
from astra.retrieval import Document, KnowledgeBase


@dataclass
class TriageState:
    subject: str
    body: str
    classification: Classification | None = None
    retrieved: list[tuple[Document, float]] = field(default_factory=list)
    draft: str | None = None
    escalated: bool = False
    escalation_reason: str | None = None


def _decide_after_classify(state: TriageState) -> str:
    """TODO: return 'escalate' or 'retrieve' per the routing rules above."""
    raise NotImplementedError("Implement post-classification routing (Stage 3).")


def _decide_after_retrieve(state: TriageState) -> str:
    """TODO: return 'escalate' or 'draft' per the routing rules above."""
    raise NotImplementedError("Implement post-retrieval routing (Stage 3).")


def build_graph(knowledge_base: KnowledgeBase | None = None) -> Any:
    """TODO: construct and compile a LangGraph StateGraph wiring together
    classify_node -> (conditional) -> retrieve_node -> (conditional) ->
    draft_node / escalate_node, using _decide_after_classify /
    _decide_after_retrieve as the conditional-edge functions.

    Accept an optional pre-built KnowledgeBase so tests/evaluation don't
    have to rebuild the TF-IDF index for every run.
    """
    raise NotImplementedError("Build the LangGraph state graph (Stage 3).")


def run_ticket(subject: str, body: str, knowledge_base: KnowledgeBase | None = None) -> TriageState:
    """TODO: run a single ticket through the compiled graph and return the
    final TriageState. This is the function stage3/main.py and
    stage4/evaluation.py should call.
    """
    raise NotImplementedError("Implement run_ticket (Stage 3).")
