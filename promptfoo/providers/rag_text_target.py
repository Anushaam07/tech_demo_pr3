"""Promptfoo provider for testing the /text endpoint.

This endpoint extracts raw text from uploaded files without creating embeddings.
Use for testing document parsing capabilities, file type support, and text
extraction quality across various formats.

Environment variables:
- PROMPTFOO_RAG_BASE_URL
- PROMPTFOO_RAG_JWT
- PROMPTFOO_RAG_TIMEOUT
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict

DEFAULT_BASE_URL = os.getenv("PROMPTFOO_RAG_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = float(os.getenv("PROMPTFOO_RAG_TIMEOUT", "60"))
JWT_TOKEN = os.getenv("PROMPTFOO_RAG_JWT")


def call_api(prompt: str, options: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None):
    """Upload a test file to /text and return extracted text."""
    options = options or {}
    config = options.get("config", {})
    vars_ctx = (context or {}).get("vars", {})

    base_url = config.get("baseUrl", DEFAULT_BASE_URL).rstrip("/")
    endpoint = config.get("endpoint", "/text")
    url = f"{base_url}{endpoint}"

    file_id = vars_ctx.get("file_id", "promptfoo-text-test")
    entity_id = vars_ctx.get("entity_id", "promptfoo-text")
    filename = vars_ctx.get("filename", "test.txt")
    
    # Use prompt as file content
    file_content = prompt.encode("utf-8")
    
    boundary = "----PromptfooBoundary"
    body_parts = []
    
    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file_id"\r\n\r\n{file_id}\r\n')
    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="entity_id"\r\n\r\n{entity_id}\r\n')
    
    body_parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: text/plain\r\n\r\n'
    )
    
    body = "".join(body_parts).encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    if config.get("includeAuth", True) and JWT_TOKEN:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"

    request = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            raw_body = response.read().decode("utf-8")
            try:
                parsed = json.loads(raw_body)
            except json.JSONDecodeError:
                parsed = raw_body

            # Extract the text field
            if isinstance(parsed, dict):
                output = parsed.get("text", "")
            else:
                output = str(parsed)

            return {"output": output, "raw": parsed}
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="ignore")
        return {"output": "", "error": f"HTTP {err.code}: {body}"}
    except Exception as exc:
        return {"output": "", "error": str(exc)}
