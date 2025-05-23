from language_tutor.state import LanguageTutorState


def test_to_markdown_strips_html():
    state = LanguageTutorState(
        selected_language="English",
        selected_level="A1",
        selected_exercise="essay",
        generated_exercise="<b>Write</b> something",
        generated_hints="<p>hint</p>",
        writing_input="<div>Hello</div>",
        writing_mistakes="<span>mistake</span>",
        style_errors="<span>style</span>",
        recommendations="<div>rec</div>",
    )
    md = state.to_markdown()
    assert "<b>" not in md
    assert "<div>" not in md
    assert "<span>" not in md
