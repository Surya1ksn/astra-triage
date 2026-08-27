"""
Astra Triage LLM client.

`complete()` uses the "internal proxy" (astra.config.LLM_BASE_URL +
astra.config.LLM_API_KEY) when both are configured, via a plain
urllib POST — no SDK dependency. With no base URL/key set it falls back
to a deterministic offline stub, so the whole project runs without
network access. Never logs or raises the API key; failures are wrapped
in a RuntimeError with a safe message only.

Proxy contract (assumption, documented here since no real proxy exists
in this practice repo): Anthropic Messages API shape.
    POST {LLM_BASE_URL}/v1/messages
    headers: x-api-key, anthropic-version, content-type: application/json
    body: {model, system, max_tokens, messages: [{role: "user", content: prompt}]}
    response: {"content": [{"type": "text", "text": "..."}], ...}
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from astra import config


def _offline_stub(prompt: str, *, system: str = "", max_tokens: int = 512) -> str:
    """
    Deterministic, dependency-free fallback used when no LLM proxy is
    configured. Good enough to exercise the rest of the pipeline (and to
    keep golden-set evaluation runnable offline), but obviously not a
    real model.
    """
    return "[offline-stub response]\n" f"system={system!r}\n" f"prompt_preview={prompt[:200]!r}"


def _call_proxy(prompt: str, *, system: str, max_tokens: int) -> str:
    url = f"{config.LLM_BASE_URL}/v1/messages"
    if not url.lower().startswith(("http://", "https://")):
        raise RuntimeError("ASTRA_LLM_BASE_URL must be an http(s) URL")
    body = {
        "model": config.LLM_MODEL,
        "system": system,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    # S310 (both this Request and the urlopen call below): ruff can't see the
    # scheme guard above -- url is checked to be http(s) before either call,
    # so file:// and other unexpected schemes are already rejected.
    request = urllib.request.Request(  # noqa: S310
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "x-api-key": config.LLM_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"LLM proxy call failed: {type(exc).__name__}") from exc

    try:
        return payload["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("LLM proxy returned an unexpected response shape") from exc


def complete(prompt: str, *, system: str = "", max_tokens: int = 512) -> str:
    if config.LLM_BASE_URL and config.LLM_API_KEY:
        return _call_proxy(prompt, system=system, max_tokens=max_tokens)
    return _offline_stub(prompt, system=system, max_tokens=max_tokens)
