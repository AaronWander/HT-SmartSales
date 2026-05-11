#2027-04-28-zty-start
from agent.presales_policy import (
    ResolvedSlots,
    SlotAssessment,
    detect_slot_candidates,
    resolve_slots_config,
    compute_missing_required,
    merge_slot_assessments,
    slot_coverage,
    build_slot_assessment_messages,
    heuristic_slot_assessments,
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


def test_slot_assessment_prompt_only_exposes_candidate_slot_definitions():
    rs = ResolvedSlots(
        required_base=["wearing_scene", "core_needs"],
        required_for_handoff=[],
        optional=[],
        meta={
            "wearing_scene": {"label": "穿着场景", "desc": "最常穿着的场景"},
            "core_needs": {"label": "核心穿搭需求", "desc": "最想达成的穿搭效果"},
        },
    )

    messages = build_slot_assessment_messages(
        user_text="穿着场景是约会",
        resolved_slots=rs,
        candidate_slots=["wearing_scene"],
    )

    prompt = messages[1]["content"]
    assert "wearing_scene (穿着场景)" in prompt
    assert "core_needs (核心穿搭需求)" not in prompt
    assert "场景/用途只能填入场景类字段" in prompt


def test_negative_answer_counts_as_full_for_asked_slot():
    assessments = heuristic_slot_assessments(
        user_text="这个衣服是外出旅游穿，不涉及职业和通勤",
        candidate_slots=["work_context"],
    )

    assert len(assessments) == 1
    assert assessments[0].slot == "work_context"
    assert assessments[0].status == "full"
    assert assessments[0].value == "这个衣服是外出旅游穿，不涉及职业和通勤"


def test_slot_assessment_prompt_treats_negative_answers_as_valid():
    rs = ResolvedSlots(
        required_base=["work_context"],
        required_for_handoff=[],
        optional=[],
        meta={"work_context": {"label": "职业/通勤强度", "desc": "工作/通勤场景"}},
    )

    messages = build_slot_assessment_messages(
        user_text="不涉及职业和通勤",
        resolved_slots=rs,
        candidate_slots=["work_context"],
    )

    assert "明确回答“无/没有/不涉及/不需要/无要求”，这也是有效答案" in messages[1]["content"]
#2027-04-28-zty-end
