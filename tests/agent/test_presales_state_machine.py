#2027-05-04-zty-start
from agent.presales_state_machine import (
    PresalesStageInput,
    advance_presales_stage,
)


def test_state_machine_stays_in_info_collection_when_missing_required():
    transition = advance_presales_stage(
        PresalesStageInput(
            current_stage="info_collection",
            missing_required=["business_goal"],
            slot_coverage=0.0,
            answer_gate_action="clarify",
            final_response="为了给你更准确的方案，我先确认一个关键点。",
        )
    )
    assert transition.stage == "info_collection"
    assert transition.changed is False


def test_state_machine_enters_info_summarization_when_required_slots_full():
    transition = advance_presales_stage(
        PresalesStageInput(
            current_stage="info_collection",
            missing_required=[],
            slot_coverage=1.0,
            answer_gate_action="allow",
            final_response="好的，我已了解。",
        )
    )
    assert transition.stage == "info_summarization"
    assert transition.changed is True


def test_state_machine_requires_confirm_to_leave_info_summarization():
    transition = advance_presales_stage(
        PresalesStageInput(
            current_stage="info_summarization",
            missing_required=[],
            slot_coverage=1.0,
            answer_gate_action="allow",
            final_response="summary ...",
            confirm_event="",
        )
    )
    assert transition.stage == "info_summarization"
    assert transition.changed is False

    transition2 = advance_presales_stage(
        PresalesStageInput(
            current_stage="info_summarization",
            missing_required=[],
            slot_coverage=1.0,
            answer_gate_action="allow",
            final_response="summary ...",
            confirm_event="info_summary",
        )
    )
    assert transition2.stage == "proposal"
    assert transition2.changed is True


def test_state_machine_treats_proposal_as_terminal_after_proposal_sent():
    transition = advance_presales_stage(
        PresalesStageInput(
            current_stage="proposal",
            missing_required=[],
            slot_coverage=1.0,
            answer_gate_action="allow",
            final_response="proposal ...",
            proposal_sent=True,
        )
    )
    assert transition.stage == "proposal"
    assert transition.changed is False
    assert transition.reason == "terminal_stage"
#2027-05-04-zty-end
