"""Promptfoo provider for testing the /embed endpoint.

This exercises file upload and embedding ingestion workflows, ensuring proper
validation, chunking, and storage. Use for testing document processing quality
and security (file type restrictions, malicious uploads, etc.).

Environment variables:
- PROMPTFOO_RAG_BASE_URL
- PROMPTFOO_RAG_JWT
- PROMPTFOO_RAG_TIMEOUT
"""
from __future__ import annotations

import io
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict

DEFAULT_BASE_URL = os.getenv("PROMPTFOO_RAG_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = float(os.getenv("PROMPTFOO_RAG_TIMEOUT", "60"))
JWT_TOKEN = os.getenv("PROMPTFOO_RAG_JWT")


def call_api(prompt: str, options: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None):
    """Upload a test file to /embed and return the response."""
    options = options or {}
    config = options.get("config", {})
    vars_ctx = (context or {}).get("vars", {})

    base_url = config.get("baseUrl", DEFAULT_BASE_URL).rstrip("/")
    endpoint = config.get("endpoint", "/embed")
    url = f"{base_url}{endpoint}"

    # Build multipart form data
    file_id = vars_ctx.get("file_id", "promptfoo-embed-test")
    entity_id = vars_ctx.get("entity_id", "promptfoo-embed")
    filename = vars_ctx.get("filename", "test.txt")
    
    # Use prompt as file content
    file_content = prompt.encode("utf-8")
    
    boundary = "----PromptfooBoundary"
    body_parts = []
    
    # Add form fields
    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file_id"\r\n\r\n{file_id}\r\n')
    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="entity_id"\r\n\r\n{entity_id}\r\n')
    
    # Add file
    body_parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: text/plain\r\n\r\n'
    )
    
    # Construct body
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

            # Extract status and file_id from response
            if isinstance(parsed, dict):
                status = parsed.get("status", False)
                output = f"Upload {'succeeded' if status else 'failed'}: {parsed.get('message', '')}"
            else:
                output = str(parsed)

            return {"output": output, "raw": parsed}
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="ignore")
        return {"output": "", "error": f"HTTP {err.code}: {body}"}
    except Exception as exc:
        return {"output": "", "error": str(exc)}
