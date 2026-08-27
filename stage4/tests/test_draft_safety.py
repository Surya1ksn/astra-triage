"""
Direct unit coverage for astra.draft's safety controls, independent of
the offline stub's incidental behavior (see the audit log's "safety-check
false positive" entry -- the offline stub always produces safe content in
practice, so the integration test in test_graph_and_draft.py alone never
actually exercises _looks_unsafe catching something unsafe).
"""

from unittest.mock import patch

from astra.draft import SAFE_FALLBACK_DRAFT, _build_prompt, _looks_unsafe, draft_response
from astra.retrieval import Document


def test_looks_unsafe_flags_denylisted_content():
    assert _looks_unsafe("Sure, here is your password: hunter2") is True
    assert _looks_unsafe("I have issued a refund of $50") is True
    assert _looks_unsafe("I've gone ahead and will disable 2FA for you") is True


def test_looks_unsafe_misses_tense_variation_known_limitation():
    # UNSAFE_OUTPUT_MARKERS has "disable 2fa" (present tense) but not
    # "disabled 2fa" (past tense) -- a model phrasing a completed action
    # ("I've disabled your 2FA") slips past this exact-phrase denylist.
    # Documented as a residual risk (see stage5/production_checklist.md)
    # rather than silently papered over: UNSAFE_OUTPUT_MARKERS is given,
    # fixed content, not something this stage is meant to redesign.
    assert _looks_unsafe("I've disabled 2FA on your account as requested") is False


def test_looks_unsafe_allows_normal_reply():
    assert _looks_unsafe("Thanks for reaching out, we've logged your request.") is False


def test_build_prompt_delimits_ticket_and_context():
    doc = Document(id="kb-1", title="Test doc", text="Some KB content.")
    prompt = _build_prompt("Subject line", "Body text", [doc])
    assert "<ticket>" in prompt and "</ticket>" in prompt
    assert "<retrieved_context>" in prompt and "</retrieved_context>" in prompt
    assert "Subject line" in prompt
    assert "Body text" in prompt
    assert "Some KB content." in prompt


def test_draft_response_substitutes_safe_fallback_when_model_output_is_unsafe():
    with patch("astra.draft.llm_client.complete", return_value="Here is your password: hunter2"):
        draft = draft_response("Subject", "Body", [])
    assert draft == SAFE_FALLBACK_DRAFT


def test_draft_response_returns_model_output_when_safe():
    with patch("astra.draft.llm_client.complete", return_value="Thanks, we'll look into it."):
        draft = draft_response("Subject", "Body", [])
    assert draft == "Thanks, we'll look into it."
