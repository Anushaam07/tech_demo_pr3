"""Promptfoo HTTP provider for exercising rag_api endpoints.

This script is executed by Promptfoo when a provider entry is defined like:

  providers:
    - id: file://promptfoo/providers/rag_http_target.py
      label: rag_api_query
      config:
        endpoint: /query
        method: POST
        defaultFileId: testid1

It converts the adversarial or test prompt coming from Promptfoo into an HTTP
request against the local FastAPI server. Configure the following environment
variables to control behavior without editing the file:

- PROMPTFOO_RAG_BASE_URL (default http://127.0.0.1:8000)
- PROMPTFOO_RAG_JWT (optional bearer token for secured deployments)
- PROMPTFOO_RAG_FILE_ID (default testid1)
- PROMPTFOO_RAG_ENTITY_ID (default promptfoo-tester)
- PROMPTFOO_RAG_K (default 4)
- PROMPTFOO_RAG_TIMEOUT (default 30 seconds)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict

DEFAULT_BASE_URL = os.getenv("PROMPTFOO_RAG_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_FILE_ID = os.getenv("PROMPTFOO_RAG_FILE_ID", "testid1")
DEFAULT_ENTITY_ID = os.getenv("PROMPTFOO_RAG_ENTITY_ID", "promptfoo-tester")
DEFAULT_K = int(os.getenv("PROMPTFOO_RAG_K", "4"))
DEFAULT_TIMEOUT = float(os.getenv("PROMPTFOO_RAG_TIMEOUT", "30"))
JWT_TOKEN = os.getenv("PROMPTFOO_RAG_JWT")


def _build_payload(prompt: str, config: Dict[str, Any], context: Dict[str, Any]):
    vars_ctx = (context or {}).get("vars", {})
    payload = {
        "query": prompt,
        "file_id": vars_ctx.get("file_id")
        or config.get("defaultFileId")
        or DEFAULT_FILE_ID,
        "entity_id": vars_ctx.get("entity_id")
        or config.get("defaultEntityId")
        or DEFAULT_ENTITY_ID,
        "k": vars_ctx.get("k") or config.get("defaultK") or DEFAULT_K,
    }

    body_extras = config.get("bodyExtras")
    if isinstance(body_extras, dict):
        payload.update(body_extras)

    return payload


def call_api(prompt: str, options: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None):
    options = options or {}
    config = options.get("config", {})
    base_url = config.get("baseUrl", DEFAULT_BASE_URL).rstrip("/")
    endpoint = config.get("endpoint", "/query")
    method = config.get("method", "POST").upper()
    url = f"{base_url}{endpoint}"

    payload = _build_payload(prompt, config, context or {})
    data = json.dumps(payload).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if config.get("includeAuth", True) and JWT_TOKEN:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            raw_body = response.read().decode("utf-8")
            try:
                parsed = json.loads(raw_body)
            except json.JSONDecodeError:
                parsed = raw_body

            output = _extract_text(parsed)
            return {"output": output, "raw": parsed}
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="ignore")
        return {"output": "", "error": f"HTTP {err.code}: {body}"}
    except Exception as exc:  # pragma: no cover - defensive logging path
        return {"output": "", "error": str(exc)}


def _extract_text(parsed_response: Any) -> str:
    """Attempt to pull a representative text snippet from rag_api responses."""
    if isinstance(parsed_response, list) and parsed_response:
        first = parsed_response[0]
        if isinstance(first, list) and first:
            candidate = first[0]
            if isinstance(candidate, dict):
                return candidate.get("page_content") or json.dumps(candidate)
            return json.dumps(candidate)
        if isinstance(first, dict):
            return first.get("page_content") or json.dumps(first)
        return json.dumps(first)

    if isinstance(parsed_response, dict):
        return parsed_response.get("page_content") or json.dumps(parsed_response)

    if isinstance(parsed_response, str):
        return parsed_response

    return json.dumps(parsed_response)
