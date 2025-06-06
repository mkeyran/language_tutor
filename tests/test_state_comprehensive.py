"""Comprehensive tests for LanguageTutorState class."""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open

from language_tutor.state import LanguageTutorState, _strip_html


class TestStripHtml:
    """Tests for HTML stripping utility function."""

    def test_strip_simple_tags(self):
        text = "<p>Hello <b>world</b></p>"
        result = _strip_html(text)
        assert result == "Hello world"

    def test_strip_nested_tags(self):
        text = "<div><p>Hello <span><b>nested</b> tags</span></p></div>"
        result = _strip_html(text)
        assert result == "Hello nested tags"

    def test_strip_self_closing_tags(self):
        text = "Line 1<br/>Line 2<hr>Line 3"
        result = _strip_html(text)
        assert result == "Line 1Line 2Line 3"

    def test_no_tags(self):
        text = "Plain text without tags"
        result = _strip_html(text)
        assert result == "Plain text without tags"

    def test_empty_string(self):
        result = _strip_html("")
        assert result == ""

    def test_only_tags(self):
        text = "<div><p></p></div>"
        result = _strip_html(text)
        assert result == ""

    def test_malformed_tags(self):
        text = "Hello <b>world</p> test"
        result = _strip_html(text)
        assert result == "Hello world test"


class TestLanguageTutorState:
    """Tests for LanguageTutorState dataclass."""

    def test_default_initialization(self):
        state = LanguageTutorState()
        assert state.selected_language == ""
        assert state.selected_exercise == ""
        assert state.selected_level == ""
        assert state.generated_exercise == ""
        assert state.generated_hints == ""
        assert state.writing_mistakes == ""
        assert state.style_errors == ""
        assert state.recommendations == ""
        assert state.writing_input == ""
        assert state.grammar_errors_raw == []
        assert state.style_errors_raw == []
        assert state.writing_input_html == ""

    def test_custom_initialization(self):
        state = LanguageTutorState(
            selected_language="en",
            selected_exercise="Essay",
            selected_level="B2",
            generated_exercise="Write about your hobbies",
            writing_input="I like reading books",
            grammar_errors_raw=[("error1", "explanation1")],
            style_errors_raw=[("error2", "explanation2")]
        )
        assert state.selected_language == "en"
        assert state.selected_exercise == "Essay"
        assert state.selected_level == "B2"
        assert state.generated_exercise == "Write about your hobbies"
        assert state.writing_input == "I like reading books"
        assert len(state.grammar_errors_raw) == 1
        assert len(state.style_errors_raw) == 1

    def test_to_dict(self):
        state = LanguageTutorState(
            selected_language="pl",
            selected_exercise="Letter",
            grammar_errors_raw=[("test", "error")]
        )
        result = state.to_dict()
        assert isinstance(result, dict)
        assert result["selected_language"] == "pl"
        assert result["selected_exercise"] == "Letter"
        assert result["grammar_errors_raw"] == [("test", "error")]
        assert "selected_level" in result
        assert "writing_input" in result

    def test_to_markdown_empty_state(self):
        state = LanguageTutorState()
        markdown = state.to_markdown()
        assert "# Language Tutor Export" in markdown
        assert "**Language:**" in markdown
        assert "**Level:**" in markdown
        assert "**Exercise Type:**" in markdown
        assert "## Exercise" in markdown
        assert "## Hints" in markdown
        assert "None." in markdown  # Should show "None." for empty fields

    def test_to_markdown_with_content(self):
        state = LanguageTutorState(
            selected_language="English",
            selected_level="B1",
            selected_exercise="Essay",
            generated_exercise="Write about your hometown",
            generated_hints="Use descriptive adjectives",
            writing_input="My hometown is beautiful",
            writing_mistakes="Grammar error here",
            style_errors="Style issue here",
            recommendations="Try to use more variety"
        )
        markdown = state.to_markdown()
        assert "**Language:** English" in markdown
        assert "**Level:** B1" in markdown
        assert "**Exercise Type:** Essay" in markdown
        assert "Write about your hometown" in markdown
        assert "Use descriptive adjectives" in markdown
        assert "My hometown is beautiful" in markdown
        assert "Grammar error here" in markdown
        assert "Style issue here" in markdown
        assert "Try to use more variety" in markdown

    def test_to_markdown_strips_html(self):
        state = LanguageTutorState(
            generated_exercise="<p>Write about <b>your hobbies</b></p>",
            writing_input="<div>I like <em>reading</em></div>",
            writing_mistakes="<span>Error here</span>"
        )
        markdown = state.to_markdown()
        assert "<p>" not in markdown
        assert "<b>" not in markdown
        assert "<div>" not in markdown
        assert "<em>" not in markdown
        assert "<span>" not in markdown
        assert "Write about your hobbies" in markdown
        assert "I like reading" in markdown
        assert "Error here" in markdown


class TestStatePersistence:
    """Tests for state save/load functionality."""

    def test_save_json_format(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            state = LanguageTutorState(
                selected_language="en",
                selected_exercise="Essay",
                writing_input="Test content"
            )
            state.save(temp_path)
            
            # Verify file was created and contains JSON
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                data = json.load(f)
            assert data["selected_language"] == "en"
            assert data["selected_exercise"] == "Essay"
            assert data["writing_input"] == "Test content"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_toml_format(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            state = LanguageTutorState(
                selected_language="pl",
                selected_exercise="Letter"
            )
            state.save(temp_path)
            
            # Verify file was created
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
            assert 'selected_language = "pl"' in content
            assert 'selected_exercise = "Letter"' in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_json_format(self):
        test_data = {
            "selected_language": "pt",
            "selected_exercise": "Description",
            "writing_input": "Minha cidade",
            "grammar_errors_raw": [],
            "style_errors_raw": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(test_data, tmp)
            temp_path = tmp.name
        
        try:
            state = LanguageTutorState.load(temp_path)
            assert state.selected_language == "pt"
            assert state.selected_exercise == "Description"
            assert state.writing_input == "Minha cidade"
            assert state.grammar_errors_raw == []
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_toml_format(self):
        toml_content = '''
selected_language = "en"
selected_exercise = "Story"
writing_input = "Once upon a time"
grammar_errors_raw = []
style_errors_raw = []
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as tmp:
            tmp.write(toml_content)
            temp_path = tmp.name
        
        try:
            state = LanguageTutorState.load(temp_path)
            assert state.selected_language == "en"
            assert state.selected_exercise == "Story"
            assert state.writing_input == "Once upon a time"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        # Should return default state when file doesn't exist
        state = LanguageTutorState.load("/nonexistent/path/file.json")
        assert state.selected_language == ""
        assert state.selected_exercise == ""
        assert state.writing_input == ""

    @patch('language_tutor.state.get_state_path')
    def test_save_default_path(self, mock_get_state_path):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            temp_path = tmp.name
        mock_get_state_path.return_value = temp_path
        
        try:
            state = LanguageTutorState(selected_language="test")
            state.save()  # No path specified, should use default
            
            mock_get_state_path.assert_called_once()
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch('language_tutor.state.get_state_path')
    def test_load_default_path(self, mock_get_state_path):
        test_data = {"selected_language": "default_test"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(test_data, tmp)
            temp_path = tmp.name
        mock_get_state_path.return_value = temp_path
        
        try:
            state = LanguageTutorState.load()  # No path specified
            mock_get_state_path.assert_called_once()
            assert state.selected_language == "default_test"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_roundtrip_json(self):
        """Test save and load roundtrip preserves data."""
        original_state = LanguageTutorState(
            selected_language="en",
            selected_exercise="Essay",
            selected_level="C1",
            generated_exercise="Complex topic",
            writing_input="My detailed response",
            grammar_errors_raw=[["error1", "fix1"], ["error2", "fix2"]],
            style_errors_raw=[["style1", "improvement1"]]
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            original_state.save(temp_path)
            loaded_state = LanguageTutorState.load(temp_path)
            
            assert loaded_state.selected_language == original_state.selected_language
            assert loaded_state.selected_exercise == original_state.selected_exercise
            assert loaded_state.selected_level == original_state.selected_level
            assert loaded_state.generated_exercise == original_state.generated_exercise
            assert loaded_state.writing_input == original_state.writing_input
            assert loaded_state.grammar_errors_raw == original_state.grammar_errors_raw
            assert loaded_state.style_errors_raw == original_state.style_errors_raw
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_roundtrip_toml(self):
        """Test save and load roundtrip preserves data in TOML format."""
        original_state = LanguageTutorState(
            selected_language="pl",
            selected_exercise="Letter",
            writing_input="Drogi przyjacielu"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            original_state.save(temp_path)
            loaded_state = LanguageTutorState.load(temp_path)
            
            assert loaded_state.selected_language == original_state.selected_language
            assert loaded_state.selected_exercise == original_state.selected_exercise
            assert loaded_state.writing_input == original_state.writing_input
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)