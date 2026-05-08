#2027-04-28-zty-start
"""Presales answer gating policy.

This module is intentionally free of agent-loop concerns. It receives the
current turn facts and returns a decision the caller can apply or record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from agent.presales_policy import build_low_confidence_response, next_clarify_question, next_clarify_questions


@dataclass
class AnswerGateConfig:
    enabled: bool = True
    high_slot_coverage: float = 0.8
    medium_slot_coverage: float = 0.5
    rag_failure_mode: str = "clarify_only"
    max_clarify_questions_per_turn: int = 1


@dataclass
class AnswerGateInput:
    final_response: str
    missing_slots: List[str]
    slot_coverage: float
    rag_attempted: bool
    rag_success: bool
    #2027-05-05-zty-start
    slot_meta: dict | None = None
    #2027-05-05-zty-end


@dataclass
class AnswerGateDecision:
    final_response: str
    confidence: str
    action: str
    clarify_question: str = ""
    reason: str = ""


def _bounded(value: float, default: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, out))


def evaluate_answer_gate(
    gate_input: AnswerGateInput,
    *,
    config: AnswerGateConfig,
) -> AnswerGateDecision:
    if not config.enabled:
        return AnswerGateDecision(
            final_response=gate_input.final_response,
            confidence="disabled",
            action="allow",
            reason="answer gate disabled",
        )

    coverage = _bounded(gate_input.slot_coverage, 0.0)
    high = _bounded(config.high_slot_coverage, 0.8)
    medium = min(high, _bounded(config.medium_slot_coverage, 0.5))
    missing = list(gate_input.missing_slots or [])
    max_q = max(1, int(getattr(config, "max_clarify_questions_per_turn", 1) or 1))

    final_text = str(gate_input.final_response or "").strip()

    rag_failed = (
        gate_input.rag_attempted
        and not gate_input.rag_success
        and config.rag_failure_mode == "clarify_only"
    )
    if rag_failed:
        qs = next_clarify_questions(
            missing,
            slot_meta=gate_input.slot_meta,
            slot_labels=(gate_input.slot_meta or {}).get("__template_labels__") if isinstance(gate_input.slot_meta, dict) else None,
            max_questions=max_q,
        )
        # If the model produced a real answer anyway (e.g. a general question
        # like time/weather), keep it and append clarification instead of
        # suppressing the answer entirely.
        if final_text:
            question_block = ""
            if qs:
                if len(qs) == 1:
                    question_block = qs[0]
                else:
                    question_block = "\n".join(f"{i}. {q}" for i, q in enumerate(qs, start=1))
            return AnswerGateDecision(
                final_response=(
                    f"{final_text}\n\n"
                    f"（补充说明：当前信息尚不完整，我还需要确认：\n{question_block}）"
                ).strip(),
                confidence="low",
                action="answer_with_clarify",
                clarify_question="\n".join(qs) if len(qs) > 1 else (qs[0] if qs else ""),
                reason="rag_failed_but_answered",
            )
        return AnswerGateDecision(
            final_response=build_low_confidence_response(
                missing,
                slot_meta=gate_input.slot_meta,
                slot_labels=(gate_input.slot_meta or {}).get("__template_labels__") if isinstance(gate_input.slot_meta, dict) else None,
                max_questions=max_q,
            ),
            confidence="low",
            action="clarify",
            clarify_question="\n".join(qs) if len(qs) > 1 else (qs[0] if qs else ""),
            reason="rag_failed",
        )

    if coverage >= high:
        return AnswerGateDecision(
            final_response=gate_input.final_response,
            confidence="high",
            action="allow",
            reason="slot_coverage_high",
        )

    if coverage >= medium and final_text:
        qs = next_clarify_questions(
            missing,
            slot_meta=gate_input.slot_meta,
            slot_labels=(gate_input.slot_meta or {}).get("__template_labels__") if isinstance(gate_input.slot_meta, dict) else None,
            max_questions=max_q,
        )
        question_block = ""
        if qs:
            if len(qs) == 1:
                question_block = qs[0]
            else:
                question_block = "\n".join(f"{i}. {q}" for i, q in enumerate(qs, start=1))
        return AnswerGateDecision(
            final_response=(
                f"{gate_input.final_response.strip()}\n\n"
                f"为了把方案进一步对齐，我还需要确认：\n{question_block}"
            ),
            confidence="medium",
            action="answer_with_clarify",
            clarify_question="\n".join(qs) if len(qs) > 1 else (qs[0] if qs else ""),
            reason="slot_coverage_medium",
        )

    qs = next_clarify_questions(
        missing,
        slot_meta=gate_input.slot_meta,
        slot_labels=(gate_input.slot_meta or {}).get("__template_labels__") if isinstance(gate_input.slot_meta, dict) else None,
        max_questions=max_q,
    )
    # When slot coverage is low, we still prefer to keep any substantive answer
    # and append the missing questions, rather than discarding the answer. This
    # supports "answer anytime" behavior during presales info collection.
    if final_text:
        question_block = ""
        if qs:
            if len(qs) == 1:
                question_block = qs[0]
            else:
                question_block = "\n".join(f"{i}. {q}" for i, q in enumerate(qs, start=1))
        return AnswerGateDecision(
            final_response=(
                f"{final_text}\n\n"
                f"（为了继续完善方案，我还需要确认：\n{question_block}）"
            ).strip(),
            confidence="low",
            action="answer_with_clarify",
            clarify_question="\n".join(qs) if len(qs) > 1 else (qs[0] if qs else ""),
            reason="slot_coverage_low_but_answered",
        )

        return AnswerGateDecision(
            final_response=build_low_confidence_response(
                missing,
                slot_meta=gate_input.slot_meta,
                slot_labels=(gate_input.slot_meta or {}).get("__template_labels__") if isinstance(gate_input.slot_meta, dict) else None,
                max_questions=max_q,
            ),
            confidence="low",
            action="clarify",
            clarify_question="\n".join(qs) if len(qs) > 1 else (qs[0] if qs else ""),
            reason="slot_coverage_low",
        )
#2027-04-28-zty-end
