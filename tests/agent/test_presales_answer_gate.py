#2027-04-28-zty-start
from agent.presales_answer_gate import (
    AnswerGateConfig,
    AnswerGateInput,
    evaluate_answer_gate,
)


def test_answer_gate_allows_high_confidence_response():
    decision = evaluate_answer_gate(
        AnswerGateInput(
            final_response="建议先做 PoC。",
            missing_slots=[],
            slot_coverage=0.9,
            rag_attempted=True,
            rag_success=True,
        ),
        config=AnswerGateConfig(high_slot_coverage=0.8, medium_slot_coverage=0.5),
    )

    assert decision.confidence == "high"
    assert decision.action == "allow"
    assert decision.final_response == "建议先做 PoC。"


def test_answer_gate_appends_one_clarify_question_for_medium_confidence():
    decision = evaluate_answer_gate(
        AnswerGateInput(
            final_response="可以先按销售接待场景设计方案。",
            missing_slots=["constraints", "integrations"],
            slot_coverage=0.5,
            rag_attempted=True,
            rag_success=True,
        ),
        config=AnswerGateConfig(high_slot_coverage=0.8, medium_slot_coverage=0.5),
    )

    assert decision.confidence == "medium"
    assert decision.action == "answer_with_clarify"
    assert "可以先按销售接待场景设计方案。" in decision.final_response
    assert "项目周期或预算上有什么明确约束吗？" in decision.final_response


def test_answer_gate_replaces_low_confidence_response_with_clarify():
    decision = evaluate_answer_gate(
        AnswerGateInput(
            final_response="这里给一个完整方案。",
            missing_slots=["business_goal"],
            slot_coverage=0.25,
            rag_attempted=True,
            rag_success=True,
        ),
        config=AnswerGateConfig(high_slot_coverage=0.8, medium_slot_coverage=0.5),
    )

    assert decision.confidence == "low"
    assert decision.action == "clarify"
    assert "这里给一个完整方案。" not in decision.final_response
    assert "你们这次最核心的业务目标是什么？" in decision.final_response


def test_answer_gate_rag_failure_forces_clarify_only():
    decision = evaluate_answer_gate(
        AnswerGateInput(
            final_response="我查到了政策。",
            missing_slots=[],
            slot_coverage=1.0,
            rag_attempted=True,
            rag_success=False,
        ),
        config=AnswerGateConfig(rag_failure_mode="clarify_only"),
    )

    assert decision.confidence == "low"
    assert decision.action == "clarify"
    assert "我查到了政策。" not in decision.final_response
#2027-04-28-zty-end
