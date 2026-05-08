#2027-05-04-zty-start
"""Presales proposal generator (stage: proposal).

This module generates a proposal draft from the confirmed summary data.
It is template-driven: the caller can provide a Markdown template (loaded at
startup / restart) and we will fill placeholders from slot state and optional
RAG context.

Placeholder conventions (minimal, intentionally not a full template engine):
- ``{{slot:<key>}}``: fills with a confirmed slot value (from summary_data).
- ``{{sys:<name>}}``: fills with a system value (date/time/session).
  Built-ins: date, datetime, session_id.
- ``{{rag:<query>}}``: fills with a RAG answer. The caller can supply a
  pre-fetched value or a rag_lookup callback.
- ``{{ai:<instruction>}}``: fills with model-generated text. The caller can
  supply ai_values or an ai_lookup callback. Missing -> blank.
- ``{{ext:<tool> <json_args>}}``: fills with external tool output. The caller
  can supply ext_values or an ext_lookup callback. Missing -> blank.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date as _date
from datetime import datetime as _dt
from typing import Any, Callable, Dict, Optional


def _get_slot_value(summary_data: Dict[str, Any], key: str) -> str:
    sd = summary_data if isinstance(summary_data, dict) else {}
    required = sd.get("required_base") if isinstance(sd.get("required_base"), dict) else {}
    optional = sd.get("optional") if isinstance(sd.get("optional"), dict) else {}
    entry = required.get(key) if key in required else optional.get(key)
    if isinstance(entry, dict):
        return str(entry.get("value") or "").strip()
    return ""


def _default_sys_value(name: str, *, session_id: str = "") -> str:
    key = str(name or "").strip().lower()
    if key in {"date", "today"}:
        return _date.today().isoformat()
    if key in {"datetime", "now", "now_datetime"}:
        return _dt.now().isoformat(timespec="seconds")
    if key in {"session_id", "sid"}:
        return str(session_id or "").strip()
    return ""


def default_output_path(*, session_id: str, hermes_home: str) -> str:
    """Default output file path for generated proposals.

    We keep this logic here (template module) so the business layer can stay
    deterministic and predictable across CLI/TUI/gateway.
    """
    sid = str(session_id or "default").strip() or "default"
    base = str(hermes_home or "").strip()
    if not base:
        return ""
    return f"{base.rstrip('/')}/presales/output/proposal_{sid}.generated.md"


def extract_template_placeholders(template_markdown: str) -> Dict[str, list[str]]:
    """Extract placeholder payloads from a proposal template (legacy helper).

    Returns a dict with keys: slot/sys/rag/ai/ext -> list of raw payload strings.
    Note: This helper only captures placeholders that have an explicit payload
    like ``{{rag:...}}``. For payload-less placeholders like ``{{rag}}``, use
    extract_template_placeholder_instances().
    """
    text = str(template_markdown or "")
    out: Dict[str, list[str]] = {"slot": [], "sys": [], "rag": [], "ai": [], "ext": []}
    pattern = re.compile(r"\{\{\s*(slot|sys|rag|ai|ext)\s*:\s*(.*?)\s*\}\}", re.I | re.S)
    for m in pattern.finditer(text):
        kind = str(m.group(1) or "").strip().lower()
        payload = str(m.group(2) or "").strip()
        if kind in out and payload:
            out[kind].append(payload)
    return out


def extract_template_placeholder_instances(template_markdown: str) -> list[dict]:
    """Extract placeholder instances including surrounding line context.

    Each instance is:
      {"kind": "rag|slot|sys|ai|ext", "payload": str, "line": str}

    Supports both:
    - ``{{rag:...}}`` (payload present)
    - ``{{rag}}`` / ``{{ rag }}`` (payload missing -> payload="")  for auto-intent.
    """
    text = str(template_markdown or "")
    if not text:
        return []
    pattern = re.compile(r"\{\{\s*(slot|sys|rag|ai|ext)(?:\s*:\s*(.*?))?\s*\}\}", re.I | re.S)
    instances: list[dict] = []
    for m in pattern.finditer(text):
        kind = str(m.group(1) or "").strip().lower()
        payload = str(m.group(2) or "").strip() if m.group(2) is not None else ""
        # Derive the containing line for auto-intent use cases.
        start = m.start()
        end = m.end()
        line_start = text.rfind("\n", 0, start) + 1
        line_end = text.find("\n", end)
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end]
        instances.append({"kind": kind, "payload": payload, "line": line})
    return instances


def render_template(
    *,
    template_markdown: str,
    summary_data: Dict[str, Any],
    session_id: str = "",
    sys_values: Optional[Dict[str, str]] = None,
    rag_values: Optional[Dict[str, str]] = None,
    ai_values: Optional[Dict[str, str]] = None,
    ext_values: Optional[Dict[str, str]] = None,
    sys_lookup: Optional[Callable[[str], str]] = None,
    rag_lookup: Optional[Callable[[str], str]] = None,
    ai_lookup: Optional[Callable[[str], str]] = None,
    ext_lookup: Optional[Callable[[str], str]] = None,
) -> str:
    """Render a minimal template with slot/sys/rag/ai/ext placeholders.

    Rules:
    - Missing values render as blank strings.
    - This function is intentionally side-effect free: callers can pass lookup
      callbacks that fetch from RAG/tools/models.
    """

    text = str(template_markdown or "")
    sys_values = sys_values if isinstance(sys_values, dict) else {}
    rag_values = rag_values if isinstance(rag_values, dict) else {}
    ai_values = ai_values if isinstance(ai_values, dict) else {}
    ext_values = ext_values if isinstance(ext_values, dict) else {}

    _sys_cache: Dict[str, str] = {}
    _rag_cache: Dict[str, str] = {}
    _ai_cache: Dict[str, str] = {}
    _ext_cache: Dict[str, str] = {}

    def _resolve(kind: str, payload: str) -> str:
        k = str(kind or "").strip().lower()
        p = str(payload or "").strip()
        if not p:
            return ""

        if k == "slot":
            return _get_slot_value(summary_data, p) or ""

        if k == "sys":
            if p in _sys_cache:
                return _sys_cache[p]
            if p in sys_values:
                _sys_cache[p] = str(sys_values.get(p) or "").strip()
                return _sys_cache[p]
            if sys_lookup is not None:
                try:
                    _sys_cache[p] = str(sys_lookup(p) or "").strip()
                except Exception:
                    _sys_cache[p] = ""
                return _sys_cache[p]
            _sys_cache[p] = _default_sys_value(p, session_id=session_id)
            return _sys_cache[p]

        if k == "rag":
            if p in _rag_cache:
                return _rag_cache[p]
            if p in rag_values:
                _rag_cache[p] = str(rag_values.get(p) or "").strip()
                return _rag_cache[p]
            if rag_lookup is not None:
                try:
                    _rag_cache[p] = str(rag_lookup(p) or "").strip()
                except Exception:
                    _rag_cache[p] = ""
                return _rag_cache[p]
            _rag_cache[p] = ""
            return ""

        if k == "ai":
            if p in _ai_cache:
                return _ai_cache[p]
            if p in ai_values:
                _ai_cache[p] = str(ai_values.get(p) or "").strip()
                return _ai_cache[p]
            if ai_lookup is not None:
                try:
                    _ai_cache[p] = str(ai_lookup(p) or "").strip()
                except Exception:
                    _ai_cache[p] = ""
                return _ai_cache[p]
            _ai_cache[p] = ""
            return ""

        if k == "ext":
            if p in _ext_cache:
                return _ext_cache[p]
            if p in ext_values:
                _ext_cache[p] = str(ext_values.get(p) or "").strip()
                return _ext_cache[p]
            if ext_lookup is not None:
                try:
                    _ext_cache[p] = str(ext_lookup(p) or "").strip()
                except Exception:
                    _ext_cache[p] = ""
                return _ext_cache[p]
            _ext_cache[p] = ""
            return ""

        return ""

    pattern = re.compile(r"\{\{\s*(slot|sys|rag|ai|ext)(?:\s*:\s*(.*?))?\s*\}\}", re.I | re.S)

    def _normalize_auto_intent(prefix: str) -> str:
        """Normalize payload-less {{rag}}/{{ai}} intent keys from a line prefix.

        Goal: extract a stable "field name" regardless of markdown formatting.

        Supported examples:
        - "| 身材特点简述 | {{ai}} |" -> "身材特点简述"
        - "1. 版型选择：{{ai}}" -> "版型选择"
        - "### 设计细节： {{ai}}" -> "设计细节"
        - "line_ai=版型选择：{{ai}}" -> "版型选择"  (take rhs of '=')
        - "**面料质感**：{{ai}}" -> "面料质感"
        """
        p = str(prefix or "").strip()
        if not p:
            return ""

        # If the author wrote "key=Label:{{ai}}", treat the rhs as the true label.
        if "=" in p:
            p = p.rsplit("=", 1)[-1].strip()

        # Markdown table: take the last non-empty cell.
        if "|" in p:
            cells = [c.strip() for c in p.split("|") if c.strip()]
            if cells:
                p = cells[-1]

        # Strip common markdown lead markers.
        p = re.sub(r"^\s*#{1,6}\s*", "", p)          # headings
        p = re.sub(r"^\s*>\s*", "", p)              # blockquotes
        p = re.sub(r"^\s*[-*+]\s*", "", p)          # unordered lists
        p = re.sub(r"^\s*\d+\s*[\.\)、\)]\s*", "", p)  # ordered lists

        # Remove trailing separators like ":" / "：" and surrounding whitespace.
        p = p.strip().rstrip(":：").strip()

        # Strip lightweight emphasis wrappers.
        for _ in range(2):
            if (p.startswith("**") and p.endswith("**")) or (p.startswith("__") and p.endswith("__")):
                p = p[2:-2].strip()
            elif (p.startswith("*") and p.endswith("*")) or (p.startswith("_") and p.endswith("_")):
                p = p[1:-1].strip()
            elif (p.startswith("`") and p.endswith("`")):
                p = p[1:-1].strip()

        return p.strip()

    def _line_prefix_for_match(text_: str, m_: re.Match) -> str:
        """Derive auto-intent from the containing line for payload-less {{rag}}/{{ai}}."""
        try:
            start = m_.start()
            end = m_.end()
            line_start = text_.rfind("\n", 0, start) + 1
            line_end = text_.find("\n", end)
            if line_end == -1:
                line_end = len(text_)
            line = text_[line_start:line_end]
        except Exception:
            line = ""
        raw_prefix = line.split("{{", 1)[0].strip()
        return _normalize_auto_intent(raw_prefix)

    def _repl(m):
        kind = (m.group(1) or "").strip()
        payload = m.group(2) if m.group(2) is not None else ""
        payload = str(payload or "").strip()

        # For payload-less {{rag}}/{{ai}}, derive the lookup key from line prefix so
        # upstream can populate rag_values/ai_values with stable intent keys.
        if not payload and kind.lower() in {"rag", "ai"}:
            payload = _line_prefix_for_match(text, m)
        return _resolve(kind, payload)

    text = pattern.sub(_repl, text)
    return text.strip()


@dataclass
class PresalesProposal:
    markdown: str
    data: Dict[str, Any]


def build_proposal(
    *,
    summary_data: Dict[str, Any],
    quote_context: str = "",
    template_name: str = "default",
    template_markdown: str = "",
    session_id: str = "",
    sys_values: Optional[Dict[str, str]] = None,
    rag_values: Optional[Dict[str, str]] = None,
    ai_values: Optional[Dict[str, str]] = None,
    ext_values: Optional[Dict[str, str]] = None,
    sys_lookup: Optional[Callable[[str], str]] = None,
    rag_lookup: Optional[Callable[[str], str]] = None,
    ai_lookup: Optional[Callable[[str], str]] = None,
    ext_lookup: Optional[Callable[[str], str]] = None,
) -> PresalesProposal:
    """Build a proposal markdown given confirmed summary data.

    `quote_context` should already be cleaned user-facing text (e.g. from RAG).
    """
    sd = summary_data if isinstance(summary_data, dict) else {}
    tmpl = str(template_markdown or "").strip()

    if tmpl:
        rendered = render_template(
            template_markdown=tmpl,
            summary_data=sd,
            session_id=session_id,
            sys_values=sys_values,
            rag_values=rag_values,
            ai_values=ai_values,
            ext_values=ext_values,
            sys_lookup=sys_lookup,
            rag_lookup=rag_lookup,
            ai_lookup=ai_lookup,
            ext_lookup=ext_lookup,
        )
        md = rendered
    else:
        # Backwards-compatible built-in default template.
        business_goal = _get_slot_value(sd, "business_goal")
        scenario = _get_slot_value(sd, "scenario")
        core_requirements = _get_slot_value(sd, "core_requirements")
        constraints = _get_slot_value(sd, "constraints")

        parts: list[str] = []
        parts.append("## 方案概要")
        parts.append(f"- 业务目标：{business_goal}")
        parts.append(f"- 场景：{scenario}")
        parts.append(f"- 核心需求：{core_requirements}")
        parts.append(f"- 约束：{constraints}")
        parts.append("")

        parts.append("## 推荐方案（默认草案）")
        parts.append("1. 总体架构：Hermes Agent + Gateway（Telegram）+ RAGFlow + 任务调度 + 日志监控。")
        parts.append("2. 工作流：信息采集 -> 信息整理确认 -> 方案输出并保存 -> 退出设计流程。")
        parts.append("3. 风险与边界：RAG 只用于事实/报价/政策，需求槽位只来自客户证据。")
        parts.append("")

        if quote_context.strip():
            parts.append("## 报价与成本（来自知识库/RAG）")
            parts.append(quote_context.strip())
            parts.append("")

        parts.append("## 下一步")
        parts.append("方案已生成并保存；如果需要调整，请告诉我你希望修改的点（例如预算/上线时间/集成系统/优先级）。")
        md = "\n".join(parts).strip()

    data = {
        "template": template_name,
        "summary": sd,
        "quote_context_included": bool(quote_context.strip()),
        "template_file_used": bool(tmpl),
    }
    return PresalesProposal(markdown=md, data=data)
#2027-05-04-zty-end
