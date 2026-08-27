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
- [x] No security/financial actions are ever claimed as completed.
      `SYSTEM_PROMPT` hard rules + `UNSAFE_OUTPUT_MARKERS` post-generation
      validation (defense in depth, not reliance on the model alone),
      now supplemented with `_UNSAFE_PATTERNS` regex matching that
      catches tense/morphological variants (e.g. "disabled 2fa", not
      just "disable 2fa") the original exact-phrase list missed --
      deliberately scoped to past-tense/completed-action forms so it
      doesn't re-flag `SYSTEM_PROMPT`'s own imperative language ("issue
      refunds" as something to refuse). Verified via
      `stage4/tests/test_draft_safety.py`, including a dedicated test
      that the refund pattern does NOT false-positive against the
      system prompt's own text.

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
      `python stage4/evaluation.py`; `publish-canary` requires both
      `test` AND `evaluate` to succeed, and `promote-production`
      requires `publish-canary`. Confirmed by an actual GitHub Actions
      run, not just reading the YAML (see Operability below).

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
- [x] Rollback/canary strategy defined (see deployment.md), and the
      publish/promote gate between canary and production is now a real,
      working mechanism in CI (`publish-canary` -> `promote-production`
      under separate GitHub Environments), not documentation alone.
      Real traffic-splitting and live-metric comparison remain
      documented-only -- no live orchestrator exists in this practice
      repo to automate against.
- [x] CI/CD pipeline gates deploy on tests + evaluation passing.
      **Verified with a real GitHub Actions run**, not just by reading
      the YAML: pushed to GitHub and confirmed `test`, `evaluate`,
      `publish-canary`, and `promote-production` all completed with
      `conclusion: success` (run
      https://github.com/Surya1ksn/astra-triage/actions/runs/33087018428).
      That real run caught an actual bug -- GHCR requires lowercase
      repository names but `github.repository` preserves the account's
      case -- which no amount of local review or YAML validation would
      have found; fixed and re-verified.
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
