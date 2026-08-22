# Stage 1: Pipeline Diagram (~15 min)

## Goal

Produce (or complete) a diagram of the end-to-end Astra Triage workflow
that matches what you'll implement in LangGraph during Stage 3. Do this
*before* writing orchestration code — it's meant to force you to think
through the branching logic first.

Your diagram must show, at minimum:

- Ticket input
- Ticket classification (+ confidence check)
- Knowledge retrieval
- Relevance validation (threshold check)
- Response drafting
- Conditional routing
- Escalation (and the distinct reasons a ticket can land there)
- Final output

## Starter skeleton (intentionally incomplete — finish it)

The boxes and the happy path are sketched below. You need to add the
missing escalation branches and label every decision edge with the
condition that triggers it.

```mermaid
flowchart TD
    A[Incoming ticket] --> B[Classify ticket]
    B --> C{Confidence >= threshold?}
    C -- yes --> D[Retrieve KB context]
    C -- no --> Z1[Escalate: low classification confidence]

    D --> E{Relevant context found?}
    E -- yes --> F[Draft response]
    E -- no --> Z2[Escalate: no relevant knowledge]

    %% TODO: add the branch for categories that must ALWAYS escalate
    %% regardless of confidence/retrieval (see config.ALWAYS_ESCALATE_CATEGORIES)

    F --> G[Return: classification + context + draft]

    %% TODO: unify all escalation paths into one clearly labeled output
    %% node, e.g. "Return: classification + escalation reason"
```

## Acceptance criteria for this stage

- [ ] Diagram covers all 8 required workflow elements listed above.
- [ ] All three escalation reasons are shown as distinct paths with labels:
      low classification confidence, no relevant knowledge found, and
      always-escalate category (e.g. `abuse_or_security`).
- [ ] The diagram's decision points match the conditional edges you
      actually implement in `astra/graph.py` during Stage 3 — if they
      drift apart while you build, come back and fix this file.
- [ ] Committed to git with a message like
      `docs: complete stage1 pipeline diagram`.
