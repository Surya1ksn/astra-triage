# Stage 5: Deployment (~template — complete this)

## Containerization

- [x] `Dockerfile` written (multi-stage: `python:3.11-slim` builder
      installs deps to `/install`, slim runtime copies only that plus
      `astra/` and `data/`; `.dockerignore` excludes `.venv/`, stage
      folders, docs, git metadata from the build context).
- [x] Run command and env vars documented: this is a CLI, run per ticket
      as `docker run <image> --subject "..." --body "..."`. Env vars:
      `ASTRA_LLM_BASE_URL`, `ASTRA_LLM_API_KEY`, `ASTRA_LLM_MODEL`,
      `ASTRA_CLASSIFICATION_THRESHOLD`, `ASTRA_RETRIEVAL_THRESHOLD` (see
      `.env.example`) — with none set, the container runs fully offline.
- [x] No secrets baked into the image — confirmed by inspection: the
      `Dockerfile` never references `ASTRA_LLM_API_KEY` or any secret at
      build time, only `astra/config.py` reads it at *runtime* from the
      environment.
- **Not verified**: Docker isn't installed in the environment this audit
  ran in, so `docker build`/`docker run` were never actually executed
  against this Dockerfile. Reviewed carefully but this is a real,
  documented gap — a real build/run smoke test is recommended before
  this ships anywhere.

## Deployment method

- **Trigger**: merge to `main` after CI's `test` and `evaluate` jobs
  both pass (`.github/workflows/ci.yml`'s `deploy` job has
  `needs: [test, evaluate]`, so a deploy is structurally impossible if
  either fails).
- **Target platform (assumption, stated explicitly since no real
  target exists in this practice repo)**: image is built and pushed to
  GitHub Container Registry (`ghcr.io`) by CI — that part is real and
  working. Beyond the registry, this assumes a container orchestrator
  pulls from there; picking **AWS ECS on Fargate** as the concrete
  assumption (serverless, no cluster to manage, straightforward
  task-definition image-tag swap for rollback). A real ticket-triage
  service would run as a **queue-consuming worker** (subscribed to a
  ticket-created event from the actual support platform) rather than
  the CLI wrapper shipped here — becoming a real deployed service is a
  known limitation, see PR description.
- **Deploy approval**: `environment: production` in the workflow is
  GitHub's mechanism for this, but it only takes effect once someone
  with repo admin access configures **required reviewers** on a
  `production` environment in the repo's Settings → Environments — that
  is a one-time GitHub UI/API configuration step outside this
  repository's files, not something committed code can set up. Flagging
  explicitly so it isn't mistaken for already being enforced.

## Rollback / canary strategy

- **Canary rollout**: route a small percentage of incoming tickets
  (e.g. 5%) to the new image's task set alongside the existing stable
  version for a fixed observation window (e.g. 1 hour or N tickets,
  whichever comes first). Compare, canary vs. stable, over that window:
  golden-set-equivalent accuracy on a live sample, escalation rate, and
  error/internal-error-escalation rate. Widen in stages (5% → 25% → 100%)
  only if all three stay within tolerance at each stage.
- **Automatic rollback triggers**: (1) live-sampled evaluation accuracy
  drops below the same 0.85 gate used in CI; (2) internal-error
  escalation rate (see `graph.py`'s exception-containment path) exceeds
  a small absolute threshold — even a handful is worth halting on, since
  the current architecture has no reason to ever hit that path in normal
  operation; (3) escalation rate deviates sharply in **either** direction
  from the stable baseline — a spike may mean the new version is
  failing open into escalation, but an unexpected *drop* is arguably
  worse: it can mean the new version is auto-handling tickets that
  should have been escalated (the riskier error direction identified
  during Stage 2's golden-set work — see the audit log's evaluation-rigor
  section).
- **Rollback speed and state**: rollback is a container image-tag swap
  back to the previous stable SHA — no database migrations, no
  persistent state, and no ticket data is stored by this service (each
  `run_ticket()` call is stateless; the caller owns persistence). That
  means rollback should complete in the time it takes the orchestrator
  to reschedule tasks (low single-digit minutes on Fargate) with
  **nothing to reconcile afterward** — a direct benefit of this
  service's stateless design.

## Operational SLOs

- **Availability target**: 99.5% (an internal support-ops tool, not a
  24/7 customer-facing critical path — escalation to a human is always
  the fallback if the service itself is down, which sets the bar lower
  than e.g. a payments API).
- **p95 latency**: < 3s per ticket. Offline classification + TF-IDF
  retrieval is sub-100ms; the live LLM proxy call (Stage 2's
  `_call_proxy`) is the dominant cost once a real proxy is wired in —
  this budget assumes typical hosted-LLM completion latency and should
  be re-measured against whatever real endpoint is eventually used.
- **Maximum acceptable escalation-path failure rate**: effectively zero
  — target 99.99%+ successful escalations. Escalation is this service's
  safety net; it failing silently (a ticket that should have gone to a
  human instead getting no response at all, or crashing the caller) is
  strictly worse than the happy path failing, since nothing else catches
  that failure. Page on-call on any occurrence, not just a rate
  threshold.
- **Alerting thresholds**: page if live-sampled accuracy drops below
  0.85 sustained over a rolling window; page immediately on any
  internal-error escalation (see `graph.py`); page if p95 latency
  exceeds its 3s budget for more than 5 consecutive minutes; page on any
  escalation-rate deviation beyond ±50% of the trailing 7-day baseline
  (catches both failure directions described above).
