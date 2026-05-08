from agent.presales_proposal import render_template


def test_render_template_slot_and_sys_and_missing_blanks():
    tmpl = """# Test

date={{sys:date}}
dt={{sys:datetime}}
sid={{sys:session_id}}

goal={{slot:business_goal}}
missing={{slot:does_not_exist}}

rag1={{rag:Q1}}
line_rag=版型选择：{{rag}}
rag2={{rag:Q2}}
ai1={{ai:write something}}
ext1={{ext:tool {\"x\":1}}}
"""

    summary_data = {
        "required_base": {"business_goal": {"status": "full", "value": "increase revenue"}},
        "optional": {},
    }

    out = render_template(
        template_markdown=tmpl,
        summary_data=summary_data,
        session_id="S123",
        rag_values={"Q1": "RAG-ANS", "Q2": "RAG-ANS-2"},
        # ai/ext not provided -> blank
    )

    assert "goal=increase revenue" in out
    assert "missing=" in out
    assert "rag1=RAG-ANS" in out
    # payload-less rag has no value unless caller supplies it (keep blank)
    assert "line_rag=版型选择：" in out
    assert "rag2=RAG-ANS-2" in out
    assert "sid=S123" in out
    # ai/ext placeholders should not hallucinate
    assert "ai1=" in out
    assert "ext1=" in out


def test_render_template_payloadless_ai_and_rag_use_line_prefix():
    tmpl = """# Test

line_ai=版型选择：{{ai}}
line_rag=费用：{{rag}}
"""
    summary_data = {"required_base": {}, "optional": {}}
    out = render_template(
        template_markdown=tmpl,
        summary_data=summary_data,
        session_id="S1",
        ai_values={"版型选择": "修身直筒为主，避免过紧"},
        rag_values={"费用": "整套 800 元起"},
    )
    assert "line_ai=版型选择：修身直筒为主，避免过紧" in out
    assert "line_rag=费用：整套 800 元起" in out
