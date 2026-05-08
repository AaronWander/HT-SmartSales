#2027-04-28-zty-start
"""Presales MVP policy helpers.

This module keeps presales-specific logic isolated from the core agent loop:
- slot configuration resolution (default/template/session-override)
- lightweight slot extraction from user text
- query normalization/dedup hashing
- two-tier answer gating and clarify-question generation
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Business slot lists are file-driven. Keep these empty so Hermes does not
# silently fall back to a hardcoded business domain when no slots.yaml exists.
DEFAULT_REQUIRED_BASE: List[str] = []
DEFAULT_REQUIRED_FOR_HANDOFF: List[str] = []
DEFAULT_OPTIONAL: List[str] = []


CLARIFY_PROMPTS = {
    "business_goal": "你们这次最核心的业务目标是什么？",
    "scenario": "这套能力会落在哪个具体业务场景？",
    "core_requirements": "你最优先要解决的核心需求是什么？",
    "constraints": "项目周期或预算上有什么明确约束吗？",
    "integrations": "需要和哪些现有系统做集成？",
    "success_criteria": "你们定义成功上线的标准是什么？",
    "decision_maker": "最终决策人或决策角色是谁？",
    "go_live_timeline": "期望的上线时间窗口是怎样的？",
}


# NOTE:
# We intentionally keep keyword-driven candidate detection very minimal.
# In real presales flows, many slot values are short ("蕾丝", "1000以内") and
# won't contain a keyword. The business layer should therefore prefer missing-slot
# driven evaluation rather than keyword-only matching.
SLOT_KEYWORDS = {
    # Legacy defaults kept for backward compatibility.
    "business_goal": ("目标", "增收", "降本", "转化", "留存", "效率", "业绩"),
    "scenario": ("场景", "流程", "环节", "售前", "客服", "运营", "销售"),
    "core_requirements": ("需求", "功能", "能力", "必须", "优先"),
    "constraints": ("预算", "周期", "合规", "技术栈", "限制", "约束", "截止"),
    "integrations": ("集成", "对接", "api", "crm", "erp", "系统", "数据库"),
    "success_criteria": ("成功标准", "验收", "指标", "kpi", "效果"),
    "decision_maker": ("决策", "拍板", "负责人", "老板", "采购", "审批"),
    "go_live_timeline": ("上线", "时间", "月底", "下月", "季度", "周内", "天内"),
}


@dataclass
class PresalesRuntimeConfig:
    enabled: bool = False
    state_machine_enabled: bool = True
    answer_gate_enabled: bool = True
    slot_assessment_mode: str = "llm_structured"
    slot_assessment_max_tokens: int = 1200
    # When true, proposal template RAG placeholders use an LLM to plan the
    # final ragflow query from intent + confirmed slots (instead of using the
    # raw placeholder payload as the query).
    template_rag_query_planner_enabled: bool = True
    template_rag_query_planner_max_tokens: int = 220
    # Max RAG calls when rendering proposal template placeholders (rag blocks).
    # Kept separate from the per-turn guard used during normal conversation.
    template_rag_max_calls_per_turn: int = 20
    # Max AI generations when rendering proposal template placeholders (ai blocks).
    template_ai_max_calls_per_turn: int = 8
    template_ai_max_tokens: int = 500
    template_rag_empty_render: str = ""
    output_referee_enabled: bool = True
    side_question_router_enabled: bool = True
    user_intent_classifier_enabled: bool = True
    user_intent_classifier_max_tokens: int = 160
    disable_memory_injection: bool = True
    question_generator_enabled: bool = True
    question_generator_max_tokens: int = 120
    # When true, allow the "focus-slot fallback deposit" path in run_agent.py
    # to write the user's raw reply into the last-asked slot if structured
    # assessment fails. Default off: prefer a single write path via LLM output.
    focus_slot_fallback_deposit_enabled: bool = False
    single_question_enforcement: bool = True
    # When asking missing-slot questions during info_collection, allow asking
    # multiple questions in one turn (bounded). Used when single_question_enforcement
    # is disabled and answer-gate needs to prompt for missing info efficiently.
    info_collection_questions_per_turn: int = 3
    single_retrieval_mode: bool = True
    rag_max_calls_per_turn: int = 1
    rag_dedupe_ttl_seconds: int = 600
    rag_failure_mode: str = "clarify_only"
    max_clarify_questions_per_turn: int = 1
    show_source_doc_names: bool = True
    max_visible_sources: int = 2
    high_slot_coverage: float = 0.8
    medium_slot_coverage: float = 0.5
    activation_enabled: bool = True
    activation_mode: str = "llm"
    activation_max_tokens: int = 120
    discovery_intro_enabled: bool = True
    discovery_intro_once_per_session: bool = True


@dataclass
class ResolvedSlots:
    required_base: List[str] = field(default_factory=list)
    required_for_handoff: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    #2027-05-05-zty-start
    # Optional per-slot metadata loaded from config.yaml. This is intentionally
    # lightweight so users can change slot lists/desc without code changes.
    # Format: {slot_key: {"label": "...", "desc": "..."}}
    meta: Dict[str, Dict[str, str]] = field(default_factory=dict)
    #2027-05-05-zty-end


@dataclass
class SlotAssessment:
    slot: str
    status: str
    value: str = ""
    evidence: str = ""
    confidence: float = 0.0
    reason: str = ""
    source: str = "user"


VALID_SLOT_STATUSES = {"none", "partial", "full"}

#2027-05-05-zty-start
# Slot types that can be auto-filled without user confirmation.
AUTO_TYPES = {"auto_date", "auto_datetime", "auto_now_date", "auto_now_datetime"}
#2027-05-05-zty-end


def heuristic_slot_assessments(
    *,
    user_text: str,
    candidate_slots: List[str],
) -> List[SlotAssessment]:
    """Best-effort heuristic slot extraction for common short answers.

    This is a safety net: it prevents repetitive "please provide X" loops when
    the user already answered in a compact format and the LLM structured
    assessment fails or returns invalid JSON.
    """
    text = str(user_text or "").strip()
    if not text or not candidate_slots:
        return []

    want = set(str(s or "").strip() for s in candidate_slots if str(s or "").strip())
    out: List[SlotAssessment] = []

    def _add(slot: str, value: str, evidence: str):
        if slot not in want:
            return
        v = str(value or "").strip()
        if not v:
            return
        out.append(
            SlotAssessment(
                slot=slot,
                status="full",
                value=v,
                evidence=str(evidence or text)[:200],
                confidence=0.85,
                reason="heuristic_extract",
                source="user",
            )
        )

    # Name: patterns like "姓名是赵天宇" / "叫赵天宇" / "赵天宇"
    m = re.search(r"(?:姓名|名字|称呼|我叫|叫)\s*(?:是|为)?\s*([\u4e00-\u9fffA-Za-z·•]{2,20})", text)
    if m:
        _add("customer_name", m.group(1), m.group(0))

    # Height cm
    m = re.search(r"(?:身高)\s*(?:是|为)?\s*(\d{2,3}(?:\.\d+)?)\s*(?:cm|厘米)", text, re.IGNORECASE)
    if m:
        _add("height_cm", m.group(1), m.group(0))

    # Weight kg
    m = re.search(r"(?:体重)\s*(?:是|为)?\s*(\d{2,3}(?:\.\d+)?)\s*(?:kg|公斤|千克)", text, re.IGNORECASE)
    if m:
        _add("weight_kg", m.group(1), m.group(0))

    # Budget range (very common in presales): accept compact patterns like
    # "整套700元以内" / "500-700" / "700以内". This is a fallback when the
    # structured JSON assessment fails to map the slot.
    if "budget_range" in want:
        # Require at least one number. If the user only replies "700" (no unit),
        # still accept it for budget_range because it's typically in response
        # to our budget question.
        if re.search(r"(\d+)", text):
            _add("budget_range", text, text)

    # Bust/waist/hip cm
    m = re.search(r"(?:胸围)\s*(?:是|为)?\s*(\d{2,3}(?:\.\d+)?)\s*(?:cm|厘米)?", text, re.IGNORECASE)
    if m:
        _add("bust_cm", m.group(1), m.group(0))
    m = re.search(r"(?:腰围)\s*(?:是|为)?\s*(\d{2,3}(?:\.\d+)?)\s*(?:cm|厘米)?", text, re.IGNORECASE)
    if m:
        _add("waist_cm", m.group(1), m.group(0))
    m = re.search(r"(?:臀围)\s*(?:是|为)?\s*(\d{2,3}(?:\.\d+)?)\s*(?:cm|厘米)?", text, re.IGNORECASE)
    if m:
        _add("hip_cm", m.group(1), m.group(0))

    return out


def _dedupe_keep_order(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        key = str(item or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def resolve_slots_config(
    *,
    presales_cfg: Dict[str, Any],
) -> ResolvedSlots:
    """Resolve slot config using precedence: session override > template > default."""
    slots_cfg = presales_cfg.get("slots")
    if not isinstance(slots_cfg, dict):
        slots_cfg = {}

    default_cfg = slots_cfg.get("default")
    if not isinstance(default_cfg, dict):
        default_cfg = {}

    required_base = list(default_cfg.get("required_base") or DEFAULT_REQUIRED_BASE)
    required_for_handoff = list(default_cfg.get("required_for_handoff") or DEFAULT_REQUIRED_FOR_HANDOFF)
    optional = list(default_cfg.get("optional") or DEFAULT_OPTIONAL)
    #2027-05-05-zty-start
    # Optional slot metadata mapping: {"slot_key": {"label": "...", "desc": "..."}}.
    # Users can define this in config.yaml; it is used for auto-generated
    # clarify questions and for more precise structured assessment prompts.
    meta = default_cfg.get("meta") if isinstance(default_cfg.get("meta"), dict) else {}
    meta = {str(k): (v if isinstance(v, dict) else {}) for k, v in meta.items()}
    #2027-05-05-zty-end

    session_overrides = presales_cfg.get("session_overrides")
    if not isinstance(session_overrides, dict):
        session_overrides = {}

    active_template = session_overrides.get("active_template")
    if isinstance(active_template, str) and active_template.strip():
        templates = slots_cfg.get("templates")
        if isinstance(templates, dict):
            tmpl = templates.get(active_template.strip())
            if isinstance(tmpl, dict):
                required_base = list(tmpl.get("required_base") or required_base)
                required_for_handoff = list(tmpl.get("required_for_handoff") or required_for_handoff)
                optional = list(tmpl.get("optional") or optional)
                #2027-05-05-zty-start
                tmpl_meta = tmpl.get("meta") if isinstance(tmpl.get("meta"), dict) else {}
                if tmpl_meta:
                    for k, v in tmpl_meta.items():
                        if isinstance(k, str) and isinstance(v, dict):
                            meta[k] = v
                #2027-05-05-zty-end

    add_required_base = session_overrides.get("add_required_base")
    if isinstance(add_required_base, list):
        required_base.extend([str(s) for s in add_required_base])
    remove_required_base = set(str(s) for s in (session_overrides.get("remove_required_base") or []))
    required_base = [s for s in required_base if s not in remove_required_base]

    add_optional = session_overrides.get("add_optional")
    if isinstance(add_optional, list):
        optional.extend([str(s) for s in add_optional])
    remove_optional = set(str(s) for s in (session_overrides.get("remove_optional") or []))
    optional = [s for s in optional if s not in remove_optional]

    return ResolvedSlots(
        required_base=_dedupe_keep_order(required_base),
        required_for_handoff=_dedupe_keep_order(required_for_handoff),
        optional=_dedupe_keep_order(optional),
        #2027-05-05-zty-start
        meta=meta,
        #2027-05-05-zty-end
    )


def normalized_query(text: str) -> str:
    q = str(text or "").strip().lower()
    q = re.sub(r"\s+", " ", q)
    return q


def query_hash(text: str) -> str:
    q = normalized_query(text)
    return hashlib.sha256(q.encode("utf-8")).hexdigest() if q else ""


def now_ts() -> float:
    return time.time()


def _all_resolved_slot_names(resolved_slots: ResolvedSlots) -> List[str]:
    return _dedupe_keep_order(
        resolved_slots.required_base
        + resolved_slots.required_for_handoff
        + resolved_slots.optional
        # Allow template/business-specific slot keys that are defined only in
        # metadata (common for non-default templates). Without this, structured
        # assessments for slots like "weight_kg" would be dropped as invalid.
        + list((resolved_slots.meta or {}).keys())
    )


def detect_slot_candidates(
    *,
    user_text: str,
    resolved_slots: ResolvedSlots,
) -> List[str]:
    """Return possible slots mentioned by the user.

    Candidate detection is recall only. It must never be treated as a filled
    slot because mention intent is not the same thing as usable evidence.
    """
    text = str(user_text or "").strip()
    if not text:
        return []

    lower = text.lower()
    candidates: List[str] = []
    for slot in _all_resolved_slot_names(resolved_slots):
        kws = SLOT_KEYWORDS.get(slot, ())
        if any(kw in text or kw in lower for kw in kws):
            candidates.append(slot)
    return candidates


def all_slot_names(resolved_slots: ResolvedSlots) -> List[str]:
    """Return all configured slot keys in a stable order."""
    return _all_resolved_slot_names(resolved_slots)


def extract_slots_from_user_text(
    *,
    user_text: str,
    resolved_slots: ResolvedSlots,
) -> Dict[str, str]:
    """Deprecated compatibility shim.

    Old MVP code used keyword hits as filled slots. That is unsafe for
    presales qualification, so extraction no longer fills anything.
    """
    return {}


def slot_assessment_to_dict(assessment: SlotAssessment) -> Dict[str, Any]:
    status = assessment.status if assessment.status in VALID_SLOT_STATUSES else "none"
    return {
        "status": status,
        "value": str(assessment.value or "")[:1000],
        "evidence": str(assessment.evidence or "")[:1000],
        "confidence": max(0.0, min(1.0, float(assessment.confidence or 0.0))),
        "reason": str(assessment.reason or "")[:1000],
        "source": str(assessment.source or "user")[:100],
        "updated_at": now_ts(),
    }


def _slot_entry_is_full(entry: Any) -> bool:
    return isinstance(entry, dict) and entry.get("status") == "full"


def _slot_entry_is_partial(entry: Any) -> bool:
    return isinstance(entry, dict) and entry.get("status") == "partial"


def merge_slot_assessments(
    *,
    filled_slots: Dict[str, Any],
    assessments: List[SlotAssessment],
    resolved_slots: ResolvedSlots,
) -> int:
    """Merge structured assessments into session slot state.

    Full evidence can replace existing values. Partial evidence is retained
    only when the slot is not already full. None never writes state.
    """
    if not isinstance(filled_slots, dict):
        return 0

    valid_slots = set(_all_resolved_slot_names(resolved_slots))
    changed = 0
    for assessment in assessments:
        if not isinstance(assessment, SlotAssessment):
            continue
        slot = str(assessment.slot or "").strip()
        if not slot or slot not in valid_slots:
            continue
        status = assessment.status if assessment.status in VALID_SLOT_STATUSES else "none"
        if status == "none":
            continue

        existing = filled_slots.get(slot)
        if status == "partial" and _slot_entry_is_full(existing):
            continue

        filled_slots[slot] = slot_assessment_to_dict(assessment)
        changed += 1
    return changed


def normalize_slot_value(slot: str, value: str, *, meta: Optional[Dict[str, Dict[str, str]]] = None) -> str:
    """Normalize common numeric/user formats based on slot meta."""
    def _parse_cn_num_token(tok: str) -> Optional[str]:
        """Parse a simple Chinese numeral token into an arabic number string.

        Supports common forms used in chat, mainly for 0..9999:
        - 七十五 / 一百六十五 / 两百 / 十五 / 二十
        - With decimals: 七十五点五
        Returns None when parsing fails.
        """
        t = str(tok or "").strip()
        if not t:
            return None
        # Strip units and filler words often adjacent to numbers.
        t = re.sub(r"[公斤千克斤kgKG厘米cmCM米mM度°\s]+", "", t)
        t = t.replace("公分", "").replace("左右", "").replace("大概", "").replace("大约", "")
        if not t:
            return None

        digit_map = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
        unit_map = {"十": 10, "百": 100, "千": 1000, "万": 10000}

        def _parse_int(part: str) -> Optional[int]:
            if not part:
                return 0
            # Pure digits.
            if re.fullmatch(r"\d+", part):
                try:
                    return int(part)
                except Exception:
                    return None
            total = 0
            num = 0
            unit = 1
            # Handle "十" prefix like "十五" => 10 + 5
            if part.startswith("十"):
                total += 10
                part_ = part[1:]
            else:
                part_ = part
            for ch in part_:
                if ch in digit_map:
                    num = digit_map[ch]
                elif ch in unit_map:
                    u = unit_map[ch]
                    if num == 0:
                        num = 1
                    total += num * u
                    num = 0
                else:
                    return None
            total += num
            return total

        if "点" in t:
            a, b = t.split("点", 1)
            ia = _parse_int(a)
            if ia is None:
                return None
            frac_digits: list[str] = []
            for ch in b:
                if ch in digit_map:
                    frac_digits.append(str(digit_map[ch]))
                elif ch.isdigit():
                    frac_digits.append(ch)
                else:
                    break
            if not frac_digits:
                return str(ia)
            return f"{ia}." + "".join(frac_digits)

        ia = _parse_int(t)
        return str(ia) if ia is not None else None

    s = str(slot or "").strip()
    v = str(value or "").strip()
    if not s or not v:
        return v
    meta = meta if isinstance(meta, dict) else {}
    stype = str((meta.get(s) or {}).get("type") or "").strip().lower()
    # If the slot is explicitly typed as numeric, extract the first number token.
    # Additionally, treat common numeric-slot naming conventions as numeric even
    # without meta typing. This avoids false conflicts like "我身高175" vs "175".
    # NOTE: slot keys are snake_case; we check common numeric suffixes.
    looks_numeric = bool(re.search(r"(_cm|_kg|_mm|_m|_years?|_age|_count|_num|_number)$", s.lower()))
    if stype in {"number", "float", "int", "height_cm", "weight_kg"} or looks_numeric:
        # Extract the first numeric token.
        m = re.search(r"(\d+(?:\.\d+)?)", v)
        if m:
            return m.group(1)
        # If no digits are present, try parsing a Chinese numeral token.
        # Common user inputs: "七十五公斤", "体重七十五", "一百六十五cm".
        cn = re.search(r"([零〇一二两三四五六七八九十百千万点]+)", v)
        if cn:
            parsed = _parse_cn_num_token(cn.group(1))
            if parsed is not None:
                return parsed
    return v


def slot_overwrite_policy(slot: str, *, meta: Optional[Dict[str, Dict[str, str]]] = None) -> str:
    meta = meta if isinstance(meta, dict) else {}
    pol = str((meta.get(str(slot or "").strip()) or {}).get("overwrite_policy") or "").strip().lower()
    return pol or "if_user_corrects"


def slot_conflict_policy(slot: str, *, meta: Optional[Dict[str, Dict[str, str]]] = None) -> str:
    meta = meta if isinstance(meta, dict) else {}
    pol = str((meta.get(str(slot or "").strip()) or {}).get("conflict_policy") or "").strip().lower()
    return pol or "ask_confirm"


def slot_needs_confirmation(slot: str, *, meta: Optional[Dict[str, Dict[str, str]]] = None) -> bool:
    meta = meta if isinstance(meta, dict) else {}
    raw = (meta.get(str(slot or "").strip()) or {}).get("needs_confirmation")
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return raw.strip().lower() in {"1", "true", "yes", "y", "on"}
    return False


def values_equivalent(slot: str, old_val: str, new_val: str, *, meta: Optional[Dict[str, Dict[str, str]]] = None) -> bool:
    """Heuristic equivalence check to avoid false conflict loops.

    We should only prompt the user when two values are meaningfully different.
    For many free-text slots, the model may paraphrase ("不要蕾丝" vs "避免蕾丝"),
    which should NOT trigger a conflict.
    """
    s = str(slot or "").strip()
    a = str(old_val or "").strip()
    b = str(new_val or "").strip()
    if not s or not a or not b:
        return False
    if a == b:
        return True

    meta = meta if isinstance(meta, dict) else {}
    stype = str((meta.get(s) or {}).get("type") or "").strip().lower()
    if stype in {"number", "float", "int", "height_cm", "weight_kg"}:
        # Numeric: compare extracted number token.
        ma = re.search(r"(\d+(?:\.\d+)?)", a)
        mb = re.search(r"(\d+(?:\.\d+)?)", b)
        if ma and mb:
            try:
                return float(ma.group(1)) == float(mb.group(1))
            except Exception:
                return ma.group(1) == mb.group(1)

    def _norm_text(x: str) -> str:
        x = str(x or "").strip().lower()
        # Common Chinese paraphrase tokens that shouldn't change meaning for
        # "avoid/ban" style fields.
        for w in ("不要", "别", "避免", "不想", "不希望", "不需要", "请勿", "不要有", "不太想要"):
            x = x.replace(w, "")
        # Normalize punctuation/whitespace.
        x = re.sub(r"[\s,，、;；/]+", " ", x).strip()
        return x

    return _norm_text(a) == _norm_text(b)
#2027-05-07-zty-end


def parse_slot_assessment_payload(
    payload: str,
    *,
    resolved_slots: ResolvedSlots,
) -> List[SlotAssessment]:
    """Parse model JSON into validated SlotAssessment objects."""
    text = str(payload or "").strip()
    if not text:
        return []
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return []
        try:
            data = json.loads(text[start : end + 1])
        except Exception:
            return []

    raw_items = data.get("assessments") if isinstance(data, dict) else data
    if not isinstance(raw_items, list):
        return []

    valid_slots = set(_all_resolved_slot_names(resolved_slots))
    # Candidate restriction (optional): when the prompt provides a candidate list,
    # we store it as a special field on the JSON payload under "__candidates__".
    # If present, we only accept non-none statuses for those slots.
    candidates = None
    try:
        if isinstance(data, dict) and isinstance(data.get("__candidates__"), list):
            candidates = set(str(s).strip() for s in data.get("__candidates__") if str(s).strip())
    except Exception:
        candidates = None
    assessments: List[SlotAssessment] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        slot = str(item.get("slot") or "").strip()
        if slot not in valid_slots:
            continue
        status = str(item.get("status") or "none").strip().lower()
        if status not in VALID_SLOT_STATUSES:
            status = "none"
        if candidates is not None and status != "none" and slot not in candidates:
            status = "none"
        confidence_raw = item.get("confidence", 0.0)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError):
            confidence = 0.0
        assessments.append(
            SlotAssessment(
                slot=slot,
                status=status,
                value=str(item.get("value") or "").strip(),
                evidence=str(item.get("evidence") or "").strip(),
                confidence=max(0.0, min(1.0, confidence)),
                reason=str(item.get("reason") or "").strip(),
                source=str(item.get("source") or "user").strip() or "user",
            )
        )
    return assessments


def parse_slot_assessment_tool_args(
    tool_args: Any,
    *,
    resolved_slots: ResolvedSlots,
) -> List[SlotAssessment]:
    """Parse tool-call args into validated SlotAssessment objects.

    Tool args are expected to be a dict with shape:
      {"assessments": [{"slot": "...", "status": "...", "value": "...", ...}, ...]}

    This is intentionally strict: we only accept slots present in the configured
    schema (resolved_slots).
    """
    data = tool_args
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return []
    if not isinstance(data, dict):
        return []
    raw_items = data.get("assessments")
    if not isinstance(raw_items, list):
        return []

    valid_slots = set(_all_resolved_slot_names(resolved_slots))
    assessments: List[SlotAssessment] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        slot = str(item.get("slot") or "").strip()
        if slot not in valid_slots:
            continue
        status = str(item.get("status") or "none").strip().lower()
        if status not in VALID_SLOT_STATUSES:
            status = "none"
        try:
            confidence = float(item.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        assessments.append(
            SlotAssessment(
                slot=slot,
                status=status,
                value=str(item.get("value") or "").strip(),
                evidence=str(item.get("evidence") or "").strip(),
                confidence=max(0.0, min(1.0, confidence)),
                reason=str(item.get("reason") or "").strip(),
                source=str(item.get("source") or "user").strip() or "user",
            )
        )
    return assessments


def build_slot_assessment_messages(
    *,
    user_text: str,
    resolved_slots: ResolvedSlots,
    candidate_slots: List[str],
) -> List[Dict[str, str]]:
    slot_names = _all_resolved_slot_names(resolved_slots)
    slot_lines = []
    for slot in slot_names:
        #2027-05-05-zty-start
        meta = resolved_slots.meta.get(slot, {}) if isinstance(resolved_slots.meta, dict) else {}
        label = str(meta.get("label") or "").strip()
        desc = str(meta.get("desc") or meta.get("description") or "").strip()
        prompt = CLARIFY_PROMPTS.get(slot, "")
        hint = desc or prompt
        if label:
            slot_lines.append(f"- {slot} ({label}): {hint}")
        else:
            slot_lines.append(f"- {slot}: {hint}")
        #2027-05-05-zty-end

    system = (
        "你是售前需求对齐场景的槽位证据评估器。"
        "你的任务不是回答客户，而是判断客户本轮输入是否能作为槽位证据。"
        "只输出 JSON，不要输出解释性正文。"
    )
    # IMPORTANT:
    # We include BOTH:
    # - "全量槽位列表" (for schema reference / to prevent inventing keys)
    # - "本轮需重点评估的候选槽位" (the actual target set for this turn)
    # This avoids providers/models returning unrelated slots and keeps JSON mode stable.
    user = (
        "请根据客户本轮输入评估以下槽位。\n"
        "状态定义：none=没有可用信息；partial=相关但不足以作为完整判断依据；"
        "full=有明确、可引用的客户侧依据。\n"
        "重要规则：关键词命中不能直接算 full；不确定、未定、还在讨论通常是 partial；"
        "RAG/产品知识不能替代客户需求证据。\n\n"
        f"槽位列表：\n{chr(10).join(slot_lines)}\n\n"
        f"本轮需重点评估的候选槽位（只允许在这些slot上给full/partial；其他slot一律输出none）："
        f"{json.dumps(candidate_slots, ensure_ascii=False)}\n\n"
        f"客户本轮输入：\n{str(user_text or '').strip()[:4000]}\n\n"
        "输出格式：\n"
        "{\"assessments\":[{\"slot\":\"business_goal\",\"status\":\"none|partial|full\","
        "\"value\":\"归纳后的槽位值\",\"evidence\":\"客户原话中的依据\","
        "\"confidence\":0.0,\"reason\":\"简短原因\",\"source\":\"user\"}]}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def compute_missing_required(
    *,
    resolved_slots: ResolvedSlots,
    filled_slots: Dict[str, Any],
) -> List[str]:
    missing: List[str] = []
    for slot in resolved_slots.required_base:
        #2027-05-05-zty-start
        # Auto slots do not block stage transitions.
        meta = resolved_slots.meta.get(slot, {}) if isinstance(resolved_slots.meta, dict) else {}
        stype = str(meta.get("type") or "").strip().lower()
        if stype in AUTO_TYPES:
            continue
        #2027-05-05-zty-end
        val = filled_slots.get(slot)
        if not _slot_entry_is_full(val):
            missing.append(slot)
    return missing


def sort_missing_slots(
    missing_slots: List[str],
    *,
    slot_meta: Optional[Dict[str, Dict[str, str]]] = None,
    preferred_order: Optional[List[str]] = None,
) -> List[str]:
    """Sort missing slots by configured priority (ascending), then stable by name.

    Users can set `priority` per slot in config.yaml:
      presales:
        slots:
          default:
            meta:
              customer_name:
                label: "客户姓名"
                priority: 10

    Missing/invalid priorities fall back to 100.
    If `preferred_order` is provided, it is used as a secondary ordering
    signal (e.g. template markdown order). Slots not present in the preferred
    list keep their relative order by name.
    """
    meta = slot_meta if isinstance(slot_meta, dict) else {}
    items = [str(s or "").strip() for s in (missing_slots or []) if str(s or "").strip()]
    pref = [str(s or "").strip() for s in (preferred_order or []) if str(s or "").strip()]
    pref_rank = {s: i for i, s in enumerate(pref)}

    def _prio(s: str) -> int:
        raw = (meta.get(s) or {}).get("priority") if isinstance(meta.get(s), dict) else None
        try:
            return int(raw)
        except Exception:
            return 100

    # Stable sort: priority first, then key name to keep deterministic behavior.
    return sorted(items, key=lambda s: (_prio(s), pref_rank.get(s, 10_000), s))


def slot_coverage(
    *,
    resolved_slots: ResolvedSlots,
    filled_slots: Dict[str, Any],
) -> float:
    required = resolved_slots.required_base
    if not required:
        return 1.0
    ok = sum(1 for slot in required if _slot_entry_is_full(filled_slots.get(slot)))
    return ok / max(1, len(required))


#2027-05-05-zty-start
def next_clarify_question(
    missing_slots: List[str],
    *,
    slot_meta: Optional[Dict[str, Dict[str, str]]] = None,
    slot_labels: Optional[Dict[str, str]] = None,
) -> str:
    """Generate a single clarify question for the next missing slot.

    Users can define per-slot metadata in config.yaml (label/desc). When present,
    we prefer it over hardcoded prompts so changing the slot list does not
    require code edits.
    """
    if not missing_slots:
        return "为了给你更准确的建议，我先确认一个关键约束是什么？"
    slot = str(missing_slots[0] or "").strip()
    if slot_labels and isinstance(slot_labels, dict):
        lbl = str(slot_labels.get(slot) or "").strip()
        if lbl:
            return f"请补充一下 `{lbl}` 的信息？"
    if slot_meta and isinstance(slot_meta, dict):
        meta = slot_meta.get(slot) if isinstance(slot_meta.get(slot), dict) else {}
        label = str(meta.get("label") or "").strip()
        desc = str(meta.get("desc") or meta.get("description") or "").strip()
        if desc:
            # If desc is already a question, keep it; otherwise wrap it.
            if any(mark in desc for mark in ("？", "?", "请问", "是否", "多少", "怎么", "如何")):
                return desc
            if label:
                return f"请补充一下 `{label}`：{desc}"
            return f"请补充一下 `{slot}`：{desc}"

    # Backwards-compatible hardcoded prompts for the default slot set.
    return CLARIFY_PROMPTS.get(slot, "为了给你更准确的建议，我先确认一个关键约束是什么？")
#2027-05-05-zty-end


#2027-05-05-zty-start
def next_clarify_questions(
    missing_slots: List[str],
    *,
    slot_meta: Optional[Dict[str, Dict[str, str]]] = None,
    slot_labels: Optional[Dict[str, str]] = None,
    max_questions: int = 1,
) -> List[str]:
    """Generate clarify questions for the first N missing slots.

    This keeps the conversation efficient: we can ask multiple small questions
    in one turn, while still bounding verbosity and cost.
    """
    try:
        n = int(max_questions)
    except (TypeError, ValueError):
        n = 1
    n = max(1, min(8, n))

    missing = [str(s or "").strip() for s in (missing_slots or [])]
    missing = [s for s in missing if s]
    if not missing:
        return ["为了给你更准确的建议，我先确认一个关键约束是什么？"]

    out: List[str] = []
    for slot in missing[:n]:
        out.append(next_clarify_question([slot], slot_meta=slot_meta, slot_labels=slot_labels))
    return out


def build_low_confidence_response(
    missing_slots: List[str],
    *,
    slot_meta: Optional[Dict[str, Dict[str, str]]] = None,
    slot_labels: Optional[Dict[str, str]] = None,
    max_questions: int = 1,
) -> str:
    questions = next_clarify_questions(
        missing_slots,
        slot_meta=slot_meta,
        slot_labels=slot_labels,
        max_questions=max_questions,
    )
    if not questions:
        return "为了给你更准确的方案，我先确认一个关键点是什么？"
    if len(questions) == 1:
        return f"为了给你更准确的方案，我先确认一个关键点：{questions[0]}"
    lines = ["为了给你更准确的方案，我先补充确认几个关键点："]
    for i, q in enumerate(questions, start=1):
        lines.append(f"{i}. {q}")
    return "\n".join(lines)
#2027-05-05-zty-end


def build_rag_cache_context(payload: Dict[str, Any], *, max_sources: int, show_doc_names: bool) -> str:
    """Build a compact context block from a cached ragflow_completion payload."""
    if not isinstance(payload, dict) or not payload.get("success"):
        return ""
    result = payload.get("result")
    if not isinstance(result, dict):
        return ""
    answer = str(result.get("answer") or "").strip()
    refs = result.get("reference")
    source_lines: List[str] = []
    if show_doc_names and isinstance(refs, list):
        count = 0
        for r in refs:
            if not isinstance(r, dict):
                continue
            name = str(r.get("doc_name") or "").strip()
            if not name:
                continue
            source_lines.append(name)
            count += 1
            if count >= max(0, int(max_sources)):
                break

    lines = [
        "<presales-rag-cache>",
        f"answer: {answer[:2600]}",
    ]
    if source_lines:
        lines.append(f"sources: {json.dumps(source_lines, ensure_ascii=False)}")
    lines.append("</presales-rag-cache>")
    return "\n".join(lines)
#2027-04-28-zty-end
