# Astra Triage service image. Multi-stage: build stage installs Python
# dependencies, runtime stage ships only the app code + installed
# packages on a slim base -- no compilers, no .venv, no test files, no
# secrets baked in (ASTRA_LLM_API_KEY etc. are injected at run time only,
# see .env.example for the full list of expected env vars).

FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

RUN useradd --create-home --uid 1000 astra
WORKDIR /app

COPY --from=builder /install /usr/local
COPY astra/ ./astra/
COPY data/ ./data/

USER astra

# This is a CLI tool (astra/main.py), not a long-running server -- run it
# per-ticket: `docker run <image> --subject "..." --body "..."`.
# ASTRA_LLM_BASE_URL / ASTRA_LLM_API_KEY / ASTRA_LLM_MODEL and the two
# threshold env vars (see .env.example) are read at runtime; with none
# set the container runs fully offline via the built-in stub.
ENTRYPOINT ["python", "-m", "astra.main"]
