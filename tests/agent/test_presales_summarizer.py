from agent.presales_policy import ResolvedSlots
from agent.presales_summarizer import build_presales_summary


def test_presales_summary_uses_labels_in_user_visible_markdown():
    summary = build_presales_summary(
        slots_state={
            "customer_name": {"status": "full", "value": "李盛新"},
            "model_file_type": {"status": "full", "value": "stl"},
            "print_dimensions_lwh": {"status": "full", "value": "30x20x10 cm"},
        },
        resolved_slots=ResolvedSlots(
            required_base=["customer_name", "model_file_type", "print_dimensions_lwh"],
            required_for_handoff=[],
            optional=[],
            meta={
                "customer_name": {"label": "客户姓名"},
                "model_file_type": {"label": "模型文件类型"},
                "print_dimensions_lwh": {"label": "打印尺寸"},
            },
        ),
        missing_required=[],
    )

    assert "必填信息（required_base）" not in summary.markdown
    assert "`customer_name`" not in summary.markdown
    assert "`model_file_type`" not in summary.markdown
    assert "`print_dimensions_lwh`" not in summary.markdown
    assert "- 客户姓名：李盛新" in summary.markdown
    assert "- 模型文件类型：stl" in summary.markdown
    assert "- 打印尺寸：30x20x10 cm" in summary.markdown
    assert summary.data["required_base"]["customer_name"]["value"] == "李盛新"


def test_presales_summary_missing_list_uses_labels():
    summary = build_presales_summary(
        slots_state={
            "customer_name": {"status": "full", "value": "李盛新"},
        },
        resolved_slots=ResolvedSlots(
            required_base=["customer_name", "delivery_method"],
            required_for_handoff=[],
            optional=[],
            meta={
                "customer_name": {"label": "客户姓名"},
                "delivery_method": {"label": "交付方式"},
            },
        ),
        missing_required=["delivery_method"],
    )

    assert "delivery_method" not in summary.markdown
    assert "交付方式" in summary.markdown
