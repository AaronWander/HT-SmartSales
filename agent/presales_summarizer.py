#2027-05-04-zty-start
"""Presales info summarization (stage: info_summarization).

This module converts filled slot evidence into a compact, user-facing summary
and a structured payload for downstream proposal generation.

Design goals:
- Deterministic: summary is derived from slot state, not free-form chat.
- Safe: never treats RAG content as user evidence; it summarizes only slots.
- Incremental: safe to re-run when the user adds corrections.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from agent.presales_policy import ResolvedSlots


@dataclass
class PresalesSummary:
    markdown: str
    data: Dict[str, Any]
    missing_required: List[str]


def _slot_entry_value(entry: Any) -> str:
    if not isinstance(entry, dict):
        return ""
    # Prefer the assessor-normalized value. Fall back to evidence for readability.
    value = str(entry.get("value") or "").strip()
    if value:
        return value
    return str(entry.get("evidence") or "").strip()


def _slot_entry_status(entry: Any) -> str:
    if not isinstance(entry, dict):
        return "none"
    return str(entry.get("status") or "none").strip().lower() or "none"


def build_presales_summary(
    *,
    slots_state: Dict[str, Any],
    resolved_slots: ResolvedSlots,
    missing_required: List[str],
    stage_hint: str = "info_summarization",
) -> PresalesSummary:
    """Build a summary from slot state.

    The summary is the "information整理" artifact the user must confirm
    naturally before we generate a proposal.
    """
    filled = slots_state if isinstance(slots_state, dict) else {}
    missing = list(missing_required or [])

    required_lines: List[str] = []
    for slot in resolved_slots.required_base:
        entry = filled.get(slot)
        status = _slot_entry_status(entry)
        value = _slot_entry_value(entry)
        if status == "full" and value:
            required_lines.append(f"- `{slot}`: {value}")
        elif status == "full":
            required_lines.append(f"- `{slot}`: (已确认)")
        elif status == "partial" and value:
            required_lines.append(f"- `{slot}`: (部分) {value}")
        else:
            required_lines.append(f"- `{slot}`: (缺失)")

    optional_lines: List[str] = []
    for slot in resolved_slots.optional:
        entry = filled.get(slot)
        status = _slot_entry_status(entry)
        value = _slot_entry_value(entry)
        if status in {"full", "partial"} and value:
            optional_lines.append(f"- `{slot}`: {value}")

    data = {
        "stage": stage_hint,
        "required_base": {
            slot: {
                "status": _slot_entry_status(filled.get(slot)),
                "value": _slot_entry_value(filled.get(slot)),
            }
            for slot in resolved_slots.required_base
        },
        "optional": {
            slot: {
                "status": _slot_entry_status(filled.get(slot)),
                "value": _slot_entry_value(filled.get(slot)),
            }
            for slot in resolved_slots.optional
        },
        "missing_required": missing,
    }

    parts: List[str] = []
    parts.append("我先把目前已收集到的信息整理如下，请你确认是否准确：")
    parts.append("")
    parts.append("**必填信息（required_base）**")
    parts.extend(required_lines or ["- (无)"])
    if optional_lines:
        parts.append("")
        parts.append("**补充信息（optional）**")
        parts.extend(optional_lines)

    parts.append("")
    if missing:
        parts.append("目前还缺少必填信息，先补齐后我再整理：")
        parts.append(f"- 缺失：{json.dumps(missing, ensure_ascii=False)}")
    else:
        parts.append("如果确认无误，请直接回复确认；如果需要修改/补充，请直接说明要调整的内容。")

    return PresalesSummary(markdown="\n".join(parts).strip(), data=data, missing_required=missing)
#2027-05-04-zty-end
