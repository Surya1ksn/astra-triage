# Stage 5: Deployment (~template — complete this)

## Containerization

- [ ] Write a `Dockerfile` for the service (multi-stage: build deps, then
      slim runtime image; don't ship the venv or test files).
- [ ] Document the run command and required env vars (`ASTRA_LLM_*`,
      thresholds).
- [ ] Confirm the container runs with no secrets baked into the image —
      they're injected at runtime only.

## Deployment method (fill in)

Describe how a new version actually gets to production. At minimum
answer:

- What triggers a deploy? (e.g. merge to `main` after CI + evaluation
  gate passes)
- What's the target platform? (pick something realistic — a container
  registry + orchestrator of your choice; state your assumption)
- Who/what can approve deploys to `production`? (see the `environment:
  production` gate in `pipeline.yml`)

## Rollback / canary strategy (fill in)

Astra Triage makes automated decisions that affect real customer tickets
(including auto-escalation and drafted responses). A bad deploy shouldn't
hit 100% of traffic instantly. Describe:

- How a canary/staged rollout would work for this service (e.g. route a
  small percentage of tickets to the new version, compare
  escalation/draft rates and evaluation metrics against the previous
  version before widening).
- What automatically triggers a rollback (e.g. evaluation score on live
  traffic sampling drops below threshold, error rate spike, escalation
  rate anomaly).
- How fast a rollback can happen and what state (if any) needs to be
  reconciled afterward.

## Operational SLOs (fill in)

Propose SLOs appropriate for a support-triage service, e.g.:

- Availability target (e.g. 99.5%)
- p95 latency target for a single ticket triage call
- Maximum acceptable escalation-path failure rate (escalation is the
  safety net — it failing silently is worse than the happy path failing)
- Alerting thresholds tied to the above
