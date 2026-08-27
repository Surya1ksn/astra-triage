# Stage 5: Production Readiness Checklist (~template — complete this)

Go through each item, mark it done/not-done, and add a one-line note on
how it's satisfied (or why it's explicitly out of scope for this
exercise).

## Security

- [x] No hardcoded secrets anywhere in source or git history.
      Removed from source in Stage 2 (`config.py`). The fake placeholder
      value (`sk-astra-DO-NOT-SHIP-THIS-...`) that remained in the
      initial scaffold commit's git history was purged with
      `git filter-repo --replace-text` and history was force-pushed;
      verified with `git log --all -p | grep` returning zero matches.
- [x] Secrets loaded from environment/CI secret store only.
      `ASTRA_LLM_API_KEY` is read via `os.environ.get(...)` and is never
      required (`None` is a supported, first-class value). CI's image
      push to GHCR uses the built-in `GITHUB_TOKEN`, so no custom secret
      is even needed for the deploy job as currently scoped.
- [x] Untrusted content never treated as instructions by the LLM.
      `draft.py` wraps ticket text and retrieved KB content in delimited
      `<ticket>`/`<retrieved_context>` blocks with an explicit system
      instruction that their contents are data, not commands. Verified
      end-to-end against the planted injection payload in
      `feature-request-process.md`.
- [~] No security/financial actions are ever claimed as completed.
      `SYSTEM_PROMPT` hard rules + `UNSAFE_OUTPUT_MARKERS` post-generation
      validation (defense in depth, not reliance on the model alone).
      **Known limitation** (caught by `stage4/tests/test_draft_safety.py`,
      added this stage): the denylist is exact-phrase, not semantic --
      it has "disable 2fa" but not "disabled 2fa", so a model phrasing a
      completed action in past tense could slip through. Documented, not
      silently fixed, since `UNSAFE_OUTPUT_MARKERS` is given/fixed
      content this exercise didn't scope for redesign. A production
      version should use broader pattern matching or a second
      classifier pass, not an exact-phrase list.

## Testing

- [x] Unit tests cover classifier, retrieval, and drafting safety checks.
      `test_classifier.py`, `test_retrieval.py`, and the new
      `test_draft_safety.py` (added this stage -- the integration test
      alone never actually exercised the denylist catching something
      unsafe, since the offline stub always produces safe content).
- [x] Integration tests cover both the auto-resolve and escalation paths.
      `test_graph_and_draft.py` (5 tests) plus manual exercise of all
      three escalation reasons and the auto-resolve path via both the
      Python API and the CLI.
- [x] Golden-set evaluation runs in CI and gates deployment.
      `.github/workflows/ci.yml`'s `evaluate` job runs
      `python stage4/evaluation.py`; `deploy` requires both `test` AND
      `evaluate` to succeed.

## Reliability

- [x] Missing/invalid LLM proxy config degrades gracefully.
      `complete()` falls back to the offline stub whenever
      `LLM_BASE_URL`/`LLM_API_KEY` aren't both set; verified.
- [x] Retrieval with zero relevant hits routes to escalation.
      `_decide_after_retrieve`; verified via unit test and the golden set.
- [x] Errors in any node are caught and routed to escalation.
      `run_ticket()` wraps the compiled graph's invocation in a
      try/except that converts any exception into an escalated
      `TriageState` (reason names the exception type only, never its
      message). Verified by injecting a fault via mocking and confirming
      escalation instead of a crash.

## Operability

- [x] SLOs defined (see deployment.md). Documented targets, not
      measured against live traffic -- there is none in this exercise.
- [x] Rollback/canary strategy defined (see deployment.md). Documented
      strategy; not automated (no live orchestrator exists to automate
      against in this practice repo).
- [x] CI/CD pipeline gates deploy on tests + evaluation passing.
      `.github/workflows/ci.yml`, verified by reading the job graph
      (`deploy: needs: [test, evaluate]`) -- not verified by an actual
      GitHub Actions run, since that requires pushing to GitHub.
- [x] Logging in place that never logs secrets or full ticket PII.
      `graph.py`'s `run_ticket()` logs category/confidence/retrieved
      count/escalated/reason only -- never subject/body text or any
      `config` value.

## Documentation

- [x] README accurately describes setup and how to run the project.
      Repo layout section updated this stage to include the Dockerfile,
      CI workflow, and audit log that didn't exist when the scaffold was
      written.
- [x] Stage 1 diagram matches the implemented graph.
      Completed and verified line-by-line against `astra/graph.py` after
      Stage 3 was built (see `stage1/diagrams/pipeline.md`).
- [x] PR description (Stage 6) completed. See `stage6/PR_DESCRIPTION.md`.
