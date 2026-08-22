"""
Astra Triage LLM client.

STAGE 2 TODO:
    Provide a single function, `complete(prompt: str, *, system: str = "",
    max_tokens: int = 512) -> str`, that:

    - Uses the "internal proxy" (astra.config.LLM_BASE_URL +
      astra.config.LLM_API_KEY) when both are set, via a plain HTTP POST
      (see `_call_proxy` stub below — fill it in, don't add a heavyweight
      SDK dependency for this).
    - Falls back to `_offline_stub` when no base URL / key is configured,
      so the whole project runs without network access.
    - Never raises on a missing key — that's a valid, supported mode.
    - Does NOT log or print the API key anywhere.

    This module is intentionally left as a stub. Wire it up.
"""

from __future__ import annotations

import json
import urllib.request

from astra import config


def _offline_stub(prompt: str, *, system: str = "", max_tokens: int = 512) -> str:
    """
    Deterministic, dependency-free fallback used when no LLM proxy is
    configured. Good enough to exercise the rest of the pipeline (and to
    keep golden-set evaluation runnable offline), but obviously not a
    real model.
    """
    return (
        "[offline-stub response]\n"
        f"system={system!r}\n"
        f"prompt_preview={prompt[:200]!r}"
    )


def _call_proxy(prompt: str, *, system: str, max_tokens: int) -> str:
    """
    TODO: implement this. It should:
      - POST to f"{config.LLM_BASE_URL}/v1/messages" (or whatever endpoint
        shape the proxy exposes — document your assumption).
      - Send the API key as a header, never as a query param or in the body
        in plaintext logs.
      - Include config.LLM_MODEL, the system prompt, the user prompt, and
        max_tokens in the request body.
      - Parse and return the text of the model's reply.
      - Raise a clear, specific exception on network/HTTP failure — don't
        let a bare exception leak the request (which may contain the key)
        into logs.

    Currently raises NotImplementedError so misconfiguration is loud
    instead of silently returning garbage.
    """
    raise NotImplementedError("Wire up the internal proxy call here (Stage 2).")


def complete(prompt: str, *, system: str = "", max_tokens: int = 512) -> str:
    if config.LLM_BASE_URL and config.LLM_API_KEY:
        return _call_proxy(prompt, system=system, max_tokens=max_tokens)
    return _offline_stub(prompt, system=system, max_tokens=max_tokens)
