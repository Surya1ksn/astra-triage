"""
Astra Triage LangGraph orchestration.

Wires classify -> route -> retrieve -> route -> draft/escalate into a
LangGraph state machine per stage1/diagrams/pipeline.md. Routing
decisions are pure functions (_decide_after_classify,
_decide_after_retrieve) independently testable from LangGraph itself;
the conditional edges just call them.

run_ticket() catches any exception raised anywhere in the graph and
converts it into an escalation rather than letting it surface to the
caller (stage5/production_checklist.md: "errors in any node are caught
and routed to escalation rather than surfacing a raw exception") --
escalation is the safety net for this service, so a bug should degrade
to "a human looks at it" rather than crash the request.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from langgraph.graph import END, StateGraph

from astra import config
from astra.classifier import Classification, classify
from astra.draft import draft_response
from astra.retrieval import Document, KnowledgeBase

logger = logging.getLogger(__name__)


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
    classification = state.classification
    if classification.category in config.ALWAYS_ESCALATE_CATEGORIES:
        return "escalate"
    if classification.confidence < config.CLASSIFICATION_THRESHOLD:
        return "escalate"
    return "retrieve"


def _decide_after_retrieve(state: TriageState) -> str:
    return "draft" if state.retrieved else "escalate"


def _classify_node(state: TriageState) -> dict:
    return {"classification": classify(state.subject, state.body)}


def _make_retrieve_node(knowledge_base: KnowledgeBase):
    def _retrieve_node(state: TriageState) -> dict:
        query = f"{state.subject}\n{state.body}"
        return {"retrieved": knowledge_base.search_relevant(query)}

    return _retrieve_node


def _draft_node(state: TriageState) -> dict:
    docs = [doc for doc, _score in state.retrieved]
    return {"draft": draft_response(state.subject, state.body, docs)}


def _escalate_node(state: TriageState) -> dict:
    classification = state.classification
    if classification is not None and classification.category in config.ALWAYS_ESCALATE_CATEGORIES:
        reason = f"category '{classification.category}' always requires human review"
    elif classification is not None and classification.confidence < config.CLASSIFICATION_THRESHOLD:
        reason = (
            f"classification confidence {classification.confidence:.2f} below "
            f"threshold {config.CLASSIFICATION_THRESHOLD:.2f}"
        )
    else:
        reason = "no relevant knowledge-base content found"
    return {"escalated": True, "escalation_reason": reason}


def build_graph(knowledge_base: KnowledgeBase | None = None) -> Any:
    kb = knowledge_base if knowledge_base is not None else KnowledgeBase()

    graph = StateGraph(TriageState)
    graph.add_node("classify_node", _classify_node)
    graph.add_node("retrieve_node", _make_retrieve_node(kb))
    graph.add_node("draft_node", _draft_node)
    graph.add_node("escalate_node", _escalate_node)

    graph.set_entry_point("classify_node")
    graph.add_conditional_edges(
        "classify_node",
        _decide_after_classify,
        {"retrieve": "retrieve_node", "escalate": "escalate_node"},
    )
    graph.add_conditional_edges(
        "retrieve_node",
        _decide_after_retrieve,
        {"draft": "draft_node", "escalate": "escalate_node"},
    )
    graph.add_edge("draft_node", END)
    graph.add_edge("escalate_node", END)

    return graph.compile()


def run_ticket(subject: str, body: str, knowledge_base: KnowledgeBase | None = None) -> TriageState:
    compiled = build_graph(knowledge_base)
    try:
        result = compiled.invoke(TriageState(subject=subject, body=body))
        state = TriageState(**result)
    except Exception as exc:
        # Deliberately broad: any node failure must escalate, not crash the request.
        logger.warning("Ticket triage failed with %s, escalating", type(exc).__name__)
        return TriageState(
            subject=subject,
            body=body,
            escalated=True,
            escalation_reason=f"internal error during triage ({type(exc).__name__})",
        )

    # Metadata only -- never log ticket subject/body (may contain customer PII)
    # or anything from config (API keys).
    logger.info(
        "Ticket triage complete: category=%s confidence=%.2f retrieved=%d escalated=%s reason=%s",
        state.classification.category if state.classification else None,
        state.classification.confidence if state.classification else 0.0,
        len(state.retrieved),
        state.escalated,
        state.escalation_reason,
    )
    return state
