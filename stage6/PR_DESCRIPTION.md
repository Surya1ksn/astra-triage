# PR: Astra Triage — implementation complete

Worked trunk-based on `main` with incremental commits per Stage 0's
guidance rather than per-stage branches (16 commits total, each scoped
to one logical change). Heavily AI-assisted with Claude Code acting as
lead developer on this task; every fix was planned, presented, and
approved before being applied, with each stage going through an
identify → fix → evaluate → test loop (re-run when a fix turned out to
be wrong or incomplete) rather than a single implement-and-move-on pass.
Full narrative, including the mistakes caught and corrected along the
way, is in `docs/Astra_Triage_Audit_Log.docx`.

## What changed

- **Config/secrets** (`astra/config.py`): removed the hardcoded API key;
  `ASTRA_LLM_API_KEY`/`BASE_URL`/`MODEL` and both thresholds now load
  from env with float validation in `[0, 1]` at import time.
- **Classifier** (`astra/classifier.py`): fixed the ranking comparison
  (`>=` → `>`) and replaced the confidence formula twice — first with a
  relative-share formula calibrated against the golden set, then again
  to require body-level (not just subject-level) keyword support after
  a subject-only coincidence produced a false-confident classification.
- **Retrieval** (`astra/retrieval.py`): implemented TF-IDF retrieval
  over sentence-level chunks (not whole documents — whole-document
  vectors under-scored real queries), with HTML comment blocks excluded
  from the index so the planted injection payload can't spuriously
  drive retrieval ranking.
- **LLM client** (`astra/llm_client.py`): implemented the live proxy
  call against an assumed Anthropic Messages API shape (documented
  assumption, no real endpoint exists to verify against), with a
  runtime URL-scheme guard.
- **Drafting** (`astra/draft.py`): implemented prompt construction with
  delimited `<ticket>`/`<retrieved_context>` blocks and post-generation
  output validation against a safety denylist.
- **Orchestration** (`astra/graph.py`): implemented the LangGraph state
  machine (classify → route → retrieve → route → draft/escalate), plus
  error containment (any node exception becomes an escalation, never a
  raw exception to the caller) and PII-safe operational logging.
- **Evaluation** (`stage4/evaluation.py`): implemented the golden-set
  harness, plus a `sys.path` fix so the documented direct-script
  invocation (`python stage4/evaluation.py`) actually works, not just
  the pytest-mediated path.
- **CI/CD**: `.github/workflows/ci.yml` — lint, test, evaluate, and a
  deploy job gated on both, with a real GHCR image push.
- **Containerization**: multi-stage `Dockerfile` + `.dockerignore`.
- **Stage 1 diagram**: completed after Stage 3, verified line-by-line
  against the actual implemented graph rather than drifting from an
  up-front sketch.
- **Security**: purged a leftover fake secret from git history
  (`git filter-repo`, force-pushed — see Remaining risks).

## Why these changes were required

Every item above ties directly to a documented bug or gap in the
original scaffold: hardcoded secret (explicit "bug #1"), broken
classification ranking and unnormalized confidence ("bug #2"), fully
stubbed retrieval/drafting/orchestration/evaluation, and an unwired
CI/CD pipeline with no real deploy safety. None were cosmetic — each
one blocked that stage's stated acceptance criteria until fixed.

## Key design decisions

- **Offline TF-IDF over a hosted embedding API**: keeps the whole
  pipeline (including CI) runnable with no network access or API key,
  per the scaffold's own design intent. Chunked at sentence level for
  scoring precision while still returning full parent documents for
  drafting context.
- **Classifier confidence = winning category's share of total keyword
  signal, gated on body-level support**: not "hits / category keyword
  count" (too low to ever clear the threshold) or a plain count (not
  normalized). Body-gating specifically prevents a subject-only
  incidental word match from producing false confidence — see the audit
  log for the exact case this caught.
- **Classification tiebreak**: first-seen category in `config.CATEGORIES`
  order wins true ties (explicit, not accidental).
- **Escalation triggers** (three, each independently testable):
  always-escalate category > low classification confidence > no
  relevant knowledge retrieved — checked in that priority order, both in
  `graph.py`'s routing and in the diagram.
- **LLM proxy contract**: assumed Anthropic Messages API shape, since no
  real internal proxy exists in this practice repo and
  `ASTRA_LLM_MODEL` already defaulted to `claude-sonnet-4-5`.

## Security controls applied

- No secrets in source (`git grep -i "sk-astra"` returns no real key) or
  in git history (verified via `git log --all -p` after the history
  purge).
- Secrets loaded from environment only, never required, never logged.
- Prompt-injection defense: retrieved KB content and ticket text are
  placed in delimited, labeled blocks with an explicit system
  instruction that their contents are data, never instructions —
  verified against the actual planted injection payload end-to-end.
- Output-side denylist (`UNSAFE_OUTPUT_MARKERS`) as defense in depth,
  independent of whether the model obeys the system prompt — with a
  documented, tested limitation (see Known limitations).
- URL-scheme validation before any outbound proxy request.

## Tests completed

25/25 passing: `test_classifier.py` (4), `test_config.py` (4),
`test_retrieval.py` (4), `test_graph_and_draft.py` (5),
`test_evaluation.py` (2), `test_draft_safety.py` (6, new this round —
direct unit coverage of the drafting safety check, previously only
exercised indirectly). Plus manual smoke exercise of the auto-resolve
path, all three escalation reasons, and a simulated node-failure fault
injection confirming error containment.

## Evaluation results

```
classification_accuracy: 1.000
routing_accuracy: 0.900
Mismatches:
  - {'id': 'account-02', 'expected_category': 'account', 'actual_category': 'account',
     'expected_outcome': 'escalate', 'actual_outcome': 'draft'}
Evaluation passed.
```

Both clear the 0.85 thresholds. The one miss is a genuinely ambiguous
case (an account/2FA ticket with real relevant KB content available) —
see the audit log's evaluation-rigor section for why this was treated as
an accepted miss rather than chased further, and for a Wilson-interval
read on how much statistical weight a 10-case golden set can actually
bear.

## Deployment readiness

CI/CD gating is real and working: `deploy` requires both `test` and
`evaluate` to pass. The image build/push to GHCR is real. Not
production-ready as-is: the canary rollout step is documented
(`stage5/deployment.md`) but not automated (no live target environment
in this practice repo), the Dockerfile was never actually
`docker build`-ed (Docker unavailable in this environment), and this is
a CLI tool, not a deployed service — becoming one needs an HTTP or
queue-worker wrapper.

## Known limitations

- Offline TF-IDF retrieval and a keyword-overlap classifier are stand-ins
  for real embeddings/ML classification — see the audit log's
  evaluation-rigor section for how these compare to published industry
  accuracy ranges.
- `UNSAFE_OUTPUT_MARKERS` is an exact-phrase denylist: it catches
  "disable 2fa" but not "disabled 2fa" (past tense) — documented and
  tested (`test_draft_safety.py`), not silently fixed, since the marker
  list is given, fixed content this exercise didn't scope for redesign.
- The offline LLM stub always resolves to the safe-fallback draft
  message (it echoes the system prompt, which trips the same denylist)
  — real generated drafts require the live proxy path, unverified here
  since no real endpoint exists to test against.
- No live-traffic canary automation — documented strategy only.
- 10-case golden set is a CI regression gate, not a statistically valid
  production-accuracy measurement (see audit log Section 5).

## Remaining risks

- `ASTRA_CLASSIFICATION_THRESHOLD` default (0.55) is below common
  industry automation-threshold practice (~0.75-0.85) — inherited from
  the original scaffold, not changed unilaterally; worth explicit
  business sign-off before real deployment.
- Git history was rewritten and force-pushed to purge a leftover fake
  secret (see audit log Section 4.5 for the full verification process).
  Confirmed safe (nothing had been pulled by anyone else), but anyone
  who had already referenced the old commit SHAs will see them changed.
- Dockerfile/CI workflow are code-reviewed but not execution-verified
  end-to-end (no Docker available locally; a real GitHub Actions run
  requires pushing to trigger).

## Rollback considerations

Application layer: this service is stateless (no persistent ticket data,
each `run_ticket()` call is independent), so rollback is a container
image-tag swap back to the previous stable SHA with nothing to
reconcile. Git layer: a full pre-rewrite backup bundle was created
before the history purge (external to the repo's own refs) in case
anything needed to be recovered.
