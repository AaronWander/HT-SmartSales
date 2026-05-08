"""RAGFlow integration tools.

This module exposes Hermes tools that call a running RAGFlow server over HTTP.

Design goals:
- Minimal coupling: treat RAGFlow as an external retrieval/QA backend.
- Hermes remains the conversation orchestrator (clarification + reporting).
- Tool returns structured JSON the model can cite and reason over.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)


def _env(name: str) -> str:
    return (os.getenv(name, "") or "").strip()


def check_ragflow_requirements() -> bool:
    """Toolset check: True when a base URL is configured."""
    return bool(_env("RAGFLOW_BASE_URL"))

def _get_primary_token(override: str | None = None) -> str | None:
    """Token used for standard /api/v1/searches* endpoints."""
    tok = (override or _env("RAGFLOW_API_TOKEN")).strip()
    return tok or None


def _get_beta_token() -> str | None:
    """Token used for /api/v1/searchbots/* endpoints in some RAGFlow builds."""
    tok = _env("RAGFLOW_BETA_TOKEN").strip()
    return tok or None


def _build_headers(api_token: str | None) -> Dict[str, str]:
    headers = {"Accept": "text/event-stream"}
    if api_token:
        # RAGFlow accepts either "Bearer <token>" or a raw token string.
        # Prefer Bearer for clarity.
        headers["Authorization"] = f"Bearer {api_token}"
    return headers


#2027-04-28-zty-start
def _build_json_headers(api_token: str | None) -> Dict[str, str]:
    headers = {"Accept": "application/json"}
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"
    return headers
#2027-04-28-zty-end


def _iter_ragflow_sse_events(resp: httpx.Response) -> List[Dict[str, Any]]:
    """Parse RAGFlow SSE response into a list of decoded JSON payloads.

    RAGFlow streams lines like:
      data:{"code":0,"message":"","data":{...}}
      data:{"code":0,"message":"","data":true}
    """
    events: List[Dict[str, Any]] = []
    for raw_line in resp.iter_lines():
        if not raw_line:
            continue
        line = raw_line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[len("data:") :].strip()
        if not payload:
            continue
        try:
            obj = json.loads(payload)
        except Exception:
            # Keep non-JSON lines for debugging; don't fail the whole call.
            events.append({"raw": payload})
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


#2027-04-28-zty-start
def _extract_search_kb_ids(search_detail_payload: Dict[str, Any]) -> List[str]:
    search_data = search_detail_payload.get("data")
    if not isinstance(search_data, dict):
        return []
    search_config = search_data.get("search_config")
    if not isinstance(search_config, dict):
        return []
    kb_ids = search_config.get("kb_ids")
    if isinstance(kb_ids, list):
        return [str(k).strip() for k in kb_ids if str(k).strip()]
    return []

def _searchbots_ask_fallback(
    *,
    client: httpx.Client,
    base: str,
    search_id: str,
    question: str,
    primary_token: str | None,
    beta_token: str | None,
) -> Dict[str, Any]:
    """Fallback for RAGFlow builds without /searches/<id>/completion.

    Strategy:
    - Use primary token to fetch search config and extract kb_ids.
    - Use beta token (if provided) to call /api/v1/searchbots/ask (SSE).

    If either token is missing, return a structured error so Hermes can
    surface a clear configuration hint.
    """
    if not beta_token:
        return {
            "success": False,
            "error": "RAGFlow server requires searchbots auth token (beta token) but RAGFLOW_BETA_TOKEN is not set.",
        }

    if not primary_token:
        return {
            "success": False,
            "error": "RAGFlow fallback requires API token to read search config but RAGFLOW_API_TOKEN is not set.",
        }

    detail_url = f"{base}/api/v1/searches/{search_id}"
    resp = client.get(detail_url, headers=_build_json_headers(primary_token))
    resp.raise_for_status()
    detail_payload = resp.json()
    if not isinstance(detail_payload, dict) or detail_payload.get("code") not in (None, 0):
        return {
            "success": False,
            "error": "Failed to fetch search config for searchbots fallback.",
            "details": (detail_payload.get("message", "") if isinstance(detail_payload, dict) else ""),
        }

    kb_ids = _extract_search_kb_ids(detail_payload)
    if not kb_ids:
        return {"success": False, "error": "No kb_ids found in search config; cannot call searchbots/ask."}

    ask_url = f"{base}/api/v1/searchbots/ask"
    body = {"question": question, "kb_ids": kb_ids}
    resp = client.post(ask_url, json=body, headers=_build_headers(beta_token))
    resp.raise_for_status()
    events = _iter_ragflow_sse_events(resp)
    # searchbots response uses {"code":..,"message":..,"data":{"answer":..,"reference":[...]}}
    completion = _extract_completion(events)
    return {"success": True, "mode": "searchbots_ask_fallback", "result": completion}


def _normalize_source_ref(item: Dict[str, Any]) -> Dict[str, Any]:
    """Keep only source metadata fields (no similarity/content payloads)."""
    if not isinstance(item, dict):
        return {}

    doc_name = (
        item.get("doc_name")
        or item.get("docnm_kwd")
        or item.get("document_name")
        or item.get("name")
        or item.get("doc")
    )
    doc_id = item.get("doc_id")
    chunk_id = item.get("chunk_id")
    dataset_id = item.get("dataset_id") or item.get("kb_id")

    ref: Dict[str, Any] = {}
    if doc_name:
        ref["doc_name"] = str(doc_name)
    if doc_id:
        ref["doc_id"] = str(doc_id)
    if chunk_id:
        ref["chunk_id"] = str(chunk_id)
    if dataset_id:
        ref["dataset_id"] = str(dataset_id)
    return ref


def _dedupe_source_refs(refs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for r in refs:
        if not isinstance(r, dict) or not r:
            continue
        key = (
            r.get("doc_name", ""),
            r.get("doc_id", ""),
            r.get("chunk_id", ""),
            r.get("dataset_id", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def _sanitize_references(reference: Any) -> List[Dict[str, Any]]:
    refs: List[Dict[str, Any]] = []
    if isinstance(reference, list):
        for item in reference:
            if isinstance(item, dict):
                refs.append(_normalize_source_ref(item))
    elif isinstance(reference, dict):
        # Typical RAGFlow structures may include either doc_aggs or chunks.
        doc_aggs = reference.get("doc_aggs")
        if isinstance(doc_aggs, list):
            for item in doc_aggs:
                if isinstance(item, dict):
                    refs.append(_normalize_source_ref(item))
        chunks = reference.get("chunks")
        if isinstance(chunks, list):
            for item in chunks:
                if isinstance(item, dict):
                    refs.append(_normalize_source_ref(item))
    return _dedupe_source_refs(refs)


def _summarize_retrieved_text(text: str, max_chars: int = 240) -> str:
    if not isinstance(text, str):
        return ""
    compact = text.replace("\\n", " ").replace("\n", " ").strip()
    compact = " ".join(compact.split())
    if not compact:
        return ""

    for sep in ("。", "！", "？", ". ", "! ", "? ", "; ", "；"):
        idx = compact.find(sep)
        if idx > 0:
            end = idx + (0 if sep.endswith(" ") else 1)
            candidate = compact[:end].strip()
            if candidate:
                return candidate[:max_chars]
    return compact[:max_chars]


def _extract_retrieval_refs(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = payload.get("data")
    if not isinstance(data, dict):
        return []
    chunks = data.get("chunks")
    if not isinstance(chunks, list):
        return []

    refs: List[Dict[str, Any]] = []
    for c in chunks:
        if not isinstance(c, dict):
            continue
        refs.append(_normalize_source_ref(c))
    return _dedupe_source_refs(refs)


def _extract_completion(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reduce event stream to a single completion payload."""
    answer: str = ""
    reference: Any = []
    #2027-04-28-zty-start
    sanitized_refs: List[Dict[str, Any]] = []
    #2027-04-28-zty-end
    last_data: Any = None
    error_message: Optional[str] = None

    for ev in events:
        if not isinstance(ev, dict):
            continue
        code = ev.get("code")
        if code not in (None, 0):
            # RAGFlow uses {code, message, data}. Preserve message for users.
            msg = ev.get("message")
            if msg:
                error_message = str(msg)
        data = ev.get("data")
        # Terminal event is typically data=true
        if data is True:
            break
        if isinstance(data, dict):
            last_data = data
            if isinstance(data.get("answer"), str):
                answer = data.get("answer") or answer
            if "reference" in data:
                reference = data.get("reference")
                #2027-04-28-zty-start
                sanitized_refs = _sanitize_references(reference)
                #2027-04-28-zty-end

    result: Dict[str, Any] = {
        "answer": answer,
        #2027-04-28-zty-start
        # "reference": reference if reference is not None else [],
        "reference": sanitized_refs,
        # "raw": last_data or {},
        "raw": {},
        #2027-04-28-zty-end
        "events": len(events),
    }
    if error_message:
        result["warning"] = error_message
    if isinstance(answer, str) and answer.strip().startswith("**ERROR**:"):
        # Many RAGFlow endpoints encode runtime errors into the answer field.
        # Mark it as a warning so Hermes can fall back to clarify-mode instead
        # of treating it as a high-confidence RAG response.
        result["warning"] = (result.get("warning") or "").strip() or answer.strip()
    return result


def _retrieval_test_fallback(
    *,
    client: httpx.Client,
    base: str,
    search_id: str,
    question: str,
    token: str | None,
) -> Dict[str, Any]:
    # 1) Get search config to resolve kb_ids.
    detail_urls = [
        f"{base}/api/v1/searches/{search_id}",
        f"{base}/v1/searches/{search_id}",
    ]
    detail_payload: Dict[str, Any] | None = None
    last_http_error: str | None = None
    for url in detail_urls:
        try:
            resp = client.get(url, headers=_build_json_headers(token))
            resp.raise_for_status()
            detail_payload = resp.json()
            break
        except httpx.HTTPStatusError as e:
            last_http_error = f"HTTP {e.response.status_code} on {url}"
            continue

    if not isinstance(detail_payload, dict):
        return {
            "success": False,
            "error": "Failed to resolve search config for fallback retrieval.",
            "details": last_http_error or "Search detail endpoint unavailable.",
        }

    if detail_payload.get("code") not in (None, 0):
        return {
            "success": False,
            "error": "Search detail request failed for fallback retrieval.",
            "details": detail_payload.get("message", ""),
        }

    kb_ids = _extract_search_kb_ids(detail_payload)
    if not kb_ids:
        return {
            "success": False,
            "error": "No kb_ids found in search config; cannot run retrieval fallback.",
        }

    # 2) Run retrieval test endpoint available in older RAGFlow API.
    retrieval_url = f"{base}/v1/chunk/retrieval_test"
    retrieval_body = {
        "search_id": search_id,
        "kb_id": kb_ids,
        "question": question,
    }
    resp = client.post(retrieval_url, json=retrieval_body, headers=_build_json_headers(token))
    resp.raise_for_status()
    retrieval_payload = resp.json()
    if not isinstance(retrieval_payload, dict):
        return {"success": False, "error": "Invalid retrieval_test response payload type."}
    if retrieval_payload.get("code") not in (None, 0):
        return {
            "success": False,
            "error": "retrieval_test returned an error.",
            "details": retrieval_payload.get("message", ""),
        }

    refs = _extract_retrieval_refs(retrieval_payload)
    top_answer = ""
    retrieval_data = retrieval_payload.get("data")
    if isinstance(retrieval_data, dict):
        chunks = retrieval_data.get("chunks")
        if isinstance(chunks, list) and chunks and isinstance(chunks[0], dict):
            best = chunks[0].get("content_with_weight") or chunks[0].get("content_ltks") or ""
            top_answer = _summarize_retrieved_text(best)

    return {
        "success": True,
        "mode": "retrieval_test_fallback",
        "result": {
            "answer": top_answer,
            "reference": refs,
            "raw": {},
            "events": 0,
            "warning": (
                "RAGFlow search completion endpoint unavailable on this server; "
                "returned retrieval results only."
            ),
        },
    }
#2027-04-28-zty-end


RAGFLOW_COMPLETION_SCHEMA = {
    "name": "ragflow_completion",
    "description": (
        "Ask a configured RAGFlow Search App to answer a question using the knowledge base, "
        "returning the answer plus citations/references for grounding. "
        "Use this for RAG-based Q&A and to decide what clarifying questions to ask.\n\n"
        "Requires RAGFLOW_BASE_URL and usually RAGFLOW_API_TOKEN. "
        "Some RAGFlow builds require a separate RAGFLOW_BETA_TOKEN for /api/v1/searchbots/* fallback. "
        "Configure a default search app via RAGFLOW_SEARCH_ID."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "User question to ask the RAGFlow search app.",
            },
            "search_id": {
                "type": "string",
                "description": "Optional override for the RAGFlow search app ID. Defaults to env RAGFLOW_SEARCH_ID.",
            },
            "base_url": {
                "type": "string",
                "description": "Optional override for the RAGFlow base URL (e.g. http://localhost:9380). Defaults to env RAGFLOW_BASE_URL.",
            },
            "api_token": {
                "type": "string",
                "description": "Optional override auth token. Defaults to env RAGFLOW_API_TOKEN.",
            },
            "timeout_seconds": {
                "type": "number",
                "description": "HTTP timeout seconds. Defaults to env RAGFLOW_TIMEOUT_SECONDS or 60.",
            },
        },
        "required": ["question"],
    },
}


def ragflow_completion(
    *,
    question: str,
    search_id: Optional[str] = None,
    base_url: Optional[str] = None,
    api_token: Optional[str] = None,
    timeout_seconds: Optional[float] = None,
    task_id: str | None = None,
) -> str:
    try:
        q = (question or "").strip()
        if not q:
            return tool_error("ragflow_completion: `question` is required.")

        base = (base_url or _env("RAGFLOW_BASE_URL")).rstrip("/")
        if not base:
            return tool_error("ragflow_completion: RAGFLOW_BASE_URL is not configured.")

        sid = (search_id or _env("RAGFLOW_SEARCH_ID")).strip()
        if not sid:
            return tool_error("ragflow_completion: `search_id` is required (or set RAGFLOW_SEARCH_ID).")

        token = _get_primary_token(api_token)
        beta_token = _get_beta_token()

        if timeout_seconds is None:
            t = _env("RAGFLOW_TIMEOUT_SECONDS")
            timeout_seconds = float(t) if t else 60.0

        url = f"{base}/api/v1/searches/{sid}/completion"
        body = {"question": q}

        timeout = httpx.Timeout(timeout_seconds)
        with httpx.Client(timeout=timeout) as client:
            #2027-04-28-zty-start
            # resp = client.post(url, json=body, headers=_build_headers(token))
            # resp.raise_for_status()
            # events = _iter_ragflow_sse_events(resp)
            # completion = _extract_completion(events)
            try:
                resp = client.post(url, json=body, headers=_build_headers(token))
                resp.raise_for_status()
                events = _iter_ragflow_sse_events(resp)
                completion = _extract_completion(events)
                mode = "search_completion"
            except httpx.HTTPStatusError as e:
                # Compatibility fallback for RAGFlow builds that expose search
                # CRUD routes but no /searches/<id>/completion endpoint.
                if e.response.status_code != 404:
                    raise
                # Prefer the newer searchbots endpoint when available, because
                # many RAGFlow builds removed /searches/<id>/completion.
                sb = _searchbots_ask_fallback(
                    client=client,
                    base=base,
                    search_id=sid,
                    question=q,
                    primary_token=token,
                    beta_token=beta_token,
                )
                if sb.get("success"):
                    completion = sb["result"]
                    mode = sb.get("mode", "searchbots_ask_fallback")
                else:
                    # Last resort: older retrieval_test endpoint (may be blocked by server permissions).
                    fallback = _retrieval_test_fallback(
                        client=client,
                        base=base,
                        search_id=sid,
                        question=q,
                        token=token,
                    )
                    if not fallback.get("success"):
                        details = (fallback.get("details", "") or "").strip()
                        hint = (sb.get("error", "") or "").strip()
                        msg = "search completion unavailable and fallbacks failed"
                        if hint:
                            msg += f": {hint}"
                        if details:
                            msg += f" ({details})"
                        raise httpx.HTTPStatusError(message=msg, request=e.request, response=e.response)
                    completion = fallback["result"]
                    mode = "retrieval_test_fallback"
            #2027-04-28-zty-end

        return json.dumps(
            {
                "success": True,
                "question": q,
                "search_id": sid,
                #2027-04-28-zty-start
                "mode": mode,
                #2027-04-28-zty-end
                "result": completion,
            },
            ensure_ascii=False,
        )
    except httpx.HTTPStatusError as e:
        text = ""
        try:
            text = e.response.text
        except Exception:
            pass
        logger.warning("ragflow_completion HTTP error: %s", e)
        return json.dumps(
            {"success": False, "error": f"HTTP {e.response.status_code}: {str(e)}", "details": text[:2000]},
            ensure_ascii=False,
        )
    except Exception as e:
        logger.exception("ragflow_completion failed: %s", e)
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def _handle_ragflow_completion(args: Dict[str, Any], **kw: Any) -> str:
    return ragflow_completion(
        question=args.get("question", ""),
        search_id=args.get("search_id"),
        base_url=args.get("base_url"),
        api_token=args.get("api_token"),
        timeout_seconds=args.get("timeout_seconds"),
        task_id=kw.get("task_id"),
    )


registry.register(
    name="ragflow_completion",
    toolset="ragflow",
    schema=RAGFLOW_COMPLETION_SCHEMA,
    handler=_handle_ragflow_completion,
    check_fn=check_ragflow_requirements,
    requires_env=["RAGFLOW_BASE_URL", "RAGFLOW_SEARCH_ID"],
    emoji="📚",
)
