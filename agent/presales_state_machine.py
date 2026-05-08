"""Presales conversation stage policy.

This module defines the deterministic stage transitions for the presales
workflow. It is intentionally free of agent-loop concerns: the caller
calculates turn facts (missing slots, confirmation events, etc.) and this
module decides which stage is next.

The state machine is deliberately conservative: one turn can advance at most
one stage, and unclear answers keep the conversation in the current stage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


#2027-05-04-zty-start
# Simplified workflow stages (strictly matches the user's flowchart):
# 1) info_collection -> 2) info_summarization -> 3) proposal
#
# NOTE: "Not in the design flow yet" is tracked outside this state machine
# (e.g. state["in_flow"]=False). We intentionally do NOT model a discovery
# stage here.
STAGE_INFO_COLLECTION = "info_collection"
STAGE_INFO_SUMMARIZATION = "info_summarization"
STAGE_PROPOSAL = "proposal"
#2027-05-04-zty-end

STAGE_ORDER = [
    STAGE_INFO_COLLECTION,
    STAGE_INFO_SUMMARIZATION,
    STAGE_PROPOSAL,
]


@dataclass
class PresalesStageInput:
    current_stage: str
    missing_required: List[str]
    slot_coverage: float
    answer_gate_action: str
    final_response: str
    #2027-05-04-zty-start
    confirm_event: str = ""  # "", "info_summary"
    proposal_sent: bool = False
    activated: bool = False
    #2027-05-04-zty-end


@dataclass
class PresalesStageTransition:
    previous_stage: str
    stage: str
    changed: bool
    reason: str = ""


def normalize_stage(stage: str) -> str:
    value = str(stage or "").strip()
    return value if value in STAGE_ORDER else STAGE_INFO_COLLECTION


def _has_actionable_answer(stage_input: PresalesStageInput) -> bool:
    if stage_input.answer_gate_action == "clarify":
        return False
    text = str(stage_input.final_response or "").strip()
    return bool(text and text != "(empty)")


def _transition(previous: str, stage: str, reason: str) -> PresalesStageTransition:
    return PresalesStageTransition(
        previous_stage=previous,
        stage=stage,
        changed=(previous != stage),
        reason=reason,
    )


def advance_presales_stage(stage_input: PresalesStageInput) -> PresalesStageTransition:
    current = normalize_stage(stage_input.current_stage)
    missing = list(stage_input.missing_required or [])
    has_answer = _has_actionable_answer(stage_input)
    confirm_event = str(stage_input.confirm_event or "").strip().lower()

    if current == STAGE_INFO_COLLECTION:
        if not missing:
            return _transition(current, STAGE_INFO_SUMMARIZATION, "required_slots_full")
        return _transition(current, current, "required_slots_missing")

    if current == STAGE_INFO_SUMMARIZATION:
        # Explicit confirmation is required to move forward.
        if confirm_event == "info_summary":
            return _transition(current, STAGE_PROPOSAL, "confirmed_info_summary")
        return _transition(current, current, "awaiting_info_summary_confirm")

    if current == STAGE_PROPOSAL:
        # Terminal stage in the simplified flowchart.
        return _transition(current, current, "terminal_stage")

    return _transition(current, current, "unknown_stage")
