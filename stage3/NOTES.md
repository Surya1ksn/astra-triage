# Stage 3: LangGraph Orchestration and Drafting (~40 min)

## Files in scope

- `astra/graph.py` — build the LangGraph state machine
- `astra/draft.py` — response drafting, with prompt-injection defenses
- `astra/main.py` — CLI entrypoint that runs a ticket through the graph

## What you're building

Wire `classify()`, `KnowledgeBase.search_relevant()`, and `draft_response()`
together into a stateful LangGraph workflow that makes an explicit
draft-vs-escalate decision — see `stage1/diagrams/pipeline.md` for the
shape it should take. Do not just call every function in a straight line
and always return a draft; the whole point is the conditional routing.

Escalation must trigger on **any** of:

- classification confidence `< config.CLASSIFICATION_THRESHOLD`
- category is in `config.ALWAYS_ESCALATE_CATEGORIES`
- `KnowledgeBase.search_relevant()` returns no hits

## Security requirement: prompt injection

`data/knowledge_base/feature-request-process.md` contains a planted
instruction-injection payload inside an HTML comment (go read it). This
simulates untrusted content making it into your retrieval context. Your
`draft_response()` implementation must not follow instructions embedded in
retrieved KB content or in the raw ticket text — only the ticket's factual
content should influence the draft, and the system prompt must clearly
separate instructions from untrusted data (e.g. wrap retrieved content and
ticket text in clearly delimited blocks and explicitly tell the model not
to treat their contents as instructions).

Test this: run a `feature_request`-category ticket through the graph and
confirm the resulting draft never mentions passwords, disabling 2FA, or
issuing a refund.

## Acceptance criteria for this stage

- [ ] `astra/graph.py` defines an explicit state type and nodes for:
      classify → route → retrieve → route → draft/escalate.
- [ ] Conditional edges implement the three escalation triggers above.
- [ ] `astra/draft.py` treats retrieved KB text and ticket text as data,
      not instructions, and the planted injection test passes.
- [ ] `astra/main.py` runs a ticket end-to-end from the CLI and prints a
      structured result (category, confidence, retrieved sources, draft
      or escalation reason).
- [ ] Both the auto-resolve path and each escalation path are manually
      exercised and behave correctly.
- [ ] Committed incrementally.
