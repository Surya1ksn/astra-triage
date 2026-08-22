# Stage 5: Production Readiness Checklist (~template — complete this)

Go through each item, mark it done/not-done, and add a one-line note on
how it's satisfied (or why it's explicitly out of scope for this
exercise).

## Security

- [ ] No hardcoded secrets anywhere in source or git history.
- [ ] Secrets loaded from environment/CI secret store only.
- [ ] Untrusted content (ticket text, retrieved KB text) never treated as
      instructions by the LLM (prompt-injection defense in `draft.py`).
- [ ] No security/financial actions (refunds, account changes) are ever
      claimed as completed by a drafted response.

## Testing

- [ ] Unit tests cover classifier, retrieval, and drafting safety checks.
- [ ] Integration tests cover both the auto-resolve and escalation paths
      through the full graph.
- [ ] Golden-set evaluation runs in CI and gates deployment.

## Reliability

- [ ] Missing/invalid LLM proxy config degrades gracefully (offline
      stub), doesn't crash the service.
- [ ] Retrieval with zero relevant hits routes to escalation instead of
      hallucinating a draft.
- [ ] Errors in any node are caught and routed to escalation rather than
      surfacing a raw exception to the caller.

## Operability

- [ ] SLOs defined (see deployment.md).
- [ ] Rollback/canary strategy defined (see deployment.md).
- [ ] CI/CD pipeline gates deploy on tests + evaluation passing.
- [ ] Logging in place that never logs secrets or full ticket PII
      unnecessarily.

## Documentation

- [ ] README accurately describes setup and how to run the project.
- [ ] Stage 1 diagram matches the implemented graph.
- [ ] PR description (Stage 6) completed.
