#2027-04-28-zty-start
from agent.presales_policy import (
    ResolvedSlots,
    SlotAssessment,
    detect_slot_candidates,
    resolve_slots_config,
    compute_missing_required,
    merge_slot_assessments,
    slot_coverage,
)


def test_resolve_slots_config_applies_template_and_session_overrides():
    cfg = {
        "slots": {
            "default": {
                "required_base": ["business_goal", "scenario"],
                "required_for_handoff": ["decision_maker"],
                "optional": ["integrations"],
            },
            "templates": {
                "enterprise": {
                    "required_base": ["business_goal", "constraints", "compliance"],
                    "required_for_handoff": ["decision_maker", "go_live_timeline"],
                }
            },
        },
        "session_overrides": {
            "active_template": "enterprise",
            "add_required_base": ["core_requirements"],
            "remove_required_base": ["compliance"],
        },
    }

    resolved = resolve_slots_config(presales_cfg=cfg)
    assert resolved.required_base == ["business_goal", "constraints", "core_requirements"]
    assert resolved.required_for_handoff == ["decision_maker", "go_live_timeline"]


def test_slot_coverage_and_missing_required():
    rs = ResolvedSlots(
        required_base=["business_goal", "scenario", "constraints"],
        required_for_handoff=[],
        optional=[],
    )
    filled = {
        "business_goal": {
            "status": "full",
            "value": "增长",
            "evidence": "目标是增长",
        },
        "constraints": {
            "status": "full",
            "value": "两个月上线",
            "evidence": "两个月上线",
        },
        "scenario": {
            "status": "partial",
            "value": "销售",
            "evidence": "销售那边可能会用",
        },
    }
    missing = compute_missing_required(resolved_slots=rs, filled_slots=filled)
    cov = slot_coverage(resolved_slots=rs, filled_slots=filled)
    assert missing == ["scenario"]
    assert abs(cov - (2 / 3)) < 1e-6


def test_keyword_candidates_do_not_mark_slots_filled():
    rs = ResolvedSlots(
        required_base=["business_goal", "constraints"],
        required_for_handoff=[],
        optional=[],
    )

    candidates = detect_slot_candidates(
        user_text="预算这个事情还没定，目标也还在讨论。",
        resolved_slots=rs,
    )

    assert candidates == ["business_goal", "constraints"]
    assert compute_missing_required(resolved_slots=rs, filled_slots={}) == [
        "business_goal",
        "constraints",
    ]
    assert slot_coverage(resolved_slots=rs, filled_slots={}) == 0.0


def test_merge_slot_assessments_only_full_counts_as_filled():
    rs = ResolvedSlots(
        required_base=["business_goal", "constraints"],
        required_for_handoff=[],
        optional=[],
    )
    state_slots = {}

    merge_slot_assessments(
        filled_slots=state_slots,
        assessments=[
            SlotAssessment(
                slot="business_goal",
                status="full",
                value="提升售前效率",
                evidence="我们想让AI先接待客户，提高售前效率",
                confidence=0.92,
                reason="明确业务目标",
            ),
            SlotAssessment(
                slot="constraints",
                status="partial",
                value="预算未定",
                evidence="预算这个事情还没定",
                confidence=0.8,
                reason="提到预算但没有明确约束",
            ),
        ],
        resolved_slots=rs,
    )

    assert state_slots["business_goal"]["status"] == "full"
    assert state_slots["constraints"]["status"] == "partial"
    assert compute_missing_required(resolved_slots=rs, filled_slots=state_slots) == ["constraints"]
    assert slot_coverage(resolved_slots=rs, filled_slots=state_slots) == 0.5
#2027-04-28-zty-end
