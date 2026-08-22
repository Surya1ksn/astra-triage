# Astra Triage — Practice Assessment Project

This is a **practice replica** of a Frontier CoE–style take-home/proctored
assessment. It is intentionally incomplete and intentionally buggy. Your job
is to open it in VS Code, use Claude Code (or any AI pair-programming tool
you like) to understand the codebase, and bring it to a "production-ready"
standard by working through Stage 0 → Stage 6 in order.

**Nobody grades this automatically for you.** Acceptance criteria are
written per-stage below and in each `stageN/` folder. Treat this the way
you'd treat the real thing: read the brief, work the stage, run the tests,
commit, move on.

## What Astra Triage is supposed to do

Astra Triage is an AI-assisted support-ticket triage service:

1. Receive an incoming support ticket (subject + body).
2. Classify it into a category (`billing`, `technical`, `account`,
   `feature_request`, `abuse_or_security`).
3. Decide whether the classification confidence is high enough to
   auto-handle.
4. Retrieve relevant knowledge-base passages for the ticket.
5. Decide whether the retrieved knowledge is actually relevant enough
   (similarity threshold).
6. If yes: draft a response grounded in the retrieved knowledge.
7. If no (low classification confidence, no relevant knowledge, or the
   category requires a human — e.g. `abuse_or_security`): escalate to a
   human with a reason.
8. Return a structured result: classification, retrieved snippets, draft
   (if any), escalation decision (if any).

## Repo layout

```
astra-triage/
├── requirements.txt          # Python deps
├── pyproject.toml            # project config, linting, pytest config
├── astra/                    # the actual importable package (fill this in)
│   ├── __init__.py
│   ├── config.py             # BROKEN: hardcoded secret, fix in Stage 2
│   ├── llm_client.py         # STUB: wire up to the "internal proxy"
│   ├── classifier.py         # BUGGY: ranking logic is wrong
│   ├── retrieval.py          # INCOMPLETE: LangChain retrieval TODOs
│   ├── draft.py              # INCOMPLETE: response drafting, Stage 3
│   ├── graph.py              # INCOMPLETE: LangGraph orchestration, Stage 3
│   └── main.py               # CLI entrypoint, Stage 3
├── data/
│   └── knowledge_base/       # markdown KB articles used for retrieval
├── stage0/GIT_USAGE.md
├── stage1/diagrams/pipeline.md
├── stage2/NOTES.md           # stage-2 specific instructions
├── stage3/NOTES.md
├── stage4/golden_set.json
├── stage4/evaluation.py
├── stage4/tests/
├── stage5/pipeline.yml
├── stage5/deployment.md
├── stage5/production_checklist.md
├── stage6/PR_DESCRIPTION.md  # template you fill in at the end
└── .env.example
```

> Note on layout: the real assessment screenshots show stage-numbered
> folders holding stage-specific *deliverables* (diagrams, docs, eval
> configs), while the actual source code lives in one evolving package
> (`astra/`) that you touch across multiple stages — that's realistic:
> production code doesn't get refactored into a new folder every sprint.
> `stageN/NOTES.md` tells you exactly which files under `astra/` are in
> scope for that stage.

## Setup

```bash
cd astra-triage
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
git init
git add .
git commit -m "chore: initial scaffold"
```

The project runs **fully offline by default** — `llm_client.py` and the
embeddings used for retrieval have local fallbacks so you can complete every
stage without any API key or network access. If you set `ASTRA_LLM_API_KEY`
and `ASTRA_LLM_BASE_URL` in `.env`, the client will use the real endpoint
instead (this mirrors the "supplied internal proxy" from the real
assessment).

## Suggested time-boxing (mirrors the real assessment, ~180 min total)

| Stage | Topic | Minutes |
|---|---|---|
| 0 | Git setup | 15 |
| 1 | Pipeline diagram | 15 |
| 2 | Config, classifier, retrieval | 45 |
| 3 | LangGraph orchestration + drafting | 40 |
| 4 | Evaluation + testing | 30 |
| 5 | CI/CD + production readiness | 25 |
| 6 | PR description | 10 |

## Working rules (to make the practice realistic)

- Only touch files relevant to the current stage unless a bug you find
  blocks that stage's acceptance criteria.
- Make small, real commits as you go — not one bulk commit at the end.
- Don't hardcode secrets. `astra/config.py` currently does — that's bug #1,
  fix it in Stage 2.
- Treat retrieved knowledge-base content and raw ticket text as **untrusted
  input** when it reaches the LLM — Stage 3 has a deliberately planted
  prompt-injection snippet in the knowledge base to test this.

Good luck — start with `stage0/GIT_USAGE.md`.
