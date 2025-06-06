"""Comprehensive tests for exercise generation and feedback functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass

from language_tutor import exercise
from language_tutor.exercise import (
    extract_content_from_xml,
    generate_exercise,
    generate_custom_hints,
    extract_annotated_errors,
    check_writing,
    format_mistakes_list
)
from language_tutor.llm import create_provider
from language_tutor.llms.base import LLM


class TestXMLExtraction:
    """Tests for XML content extraction utilities."""
    
    def test_extract_content_from_xml_basic(self):
        """Test basic XML content extraction."""
        text = "<exercise>Write about your hobbies</exercise>"
        result = extract_content_from_xml(text, "exercise")
        assert result == "Write about your hobbies"
    
    def test_extract_content_from_xml_multiline(self):
        """Test XML extraction with multiline content."""
        text = """<hints>
        Use descriptive adjectives.
        Include specific examples.
        </hints>"""
        result = extract_content_from_xml(text, "hints")
        assert "Use descriptive adjectives" in result
        assert "Include specific examples" in result
    
    def test_extract_content_from_xml_case_insensitive(self):
        """Test XML extraction is case insensitive."""
        text = "<EXERCISE>Content here</EXERCISE>"
        result = extract_content_from_xml(text, "exercise")
        assert result == "Content here"
    
    def test_extract_content_from_xml_with_nested_tags(self):
        """Test XML extraction with nested content."""
        text = "<exercise>Write about <b>your hobbies</b></exercise>"
        result = extract_content_from_xml(text, "exercise")
        assert result == "Write about <b>your hobbies</b>"
    
    def test_extract_content_from_xml_not_found(self):
        """Test XML extraction when tag not found."""
        text = "<other>Some content</other>"
        result = extract_content_from_xml(text, "exercise", "default")
        assert result == "default"
    
    def test_extract_content_from_xml_empty_content(self):
        """Test XML extraction with empty content."""
        text = "<exercise></exercise>"
        result = extract_content_from_xml(text, "exercise", "default")
        assert result == "default"
    
    def test_extract_content_from_xml_none_content(self):
        """Test XML extraction with 'None.' content."""
        text = "<hints>None.</hints>"
        result = extract_content_from_xml(text, "hints", "default")
        assert result == "default"
    
    def test_extract_content_from_xml_whitespace(self):
        """Test XML extraction handles whitespace."""
        text = "<exercise>   Write something   </exercise>"
        result = extract_content_from_xml(text, "exercise")
        assert result == "Write something"


class TestAnnotatedErrorExtraction:
    """Tests for annotated error extraction from feedback."""
    
    def test_extract_annotated_errors_basic(self):
        """Test basic error extraction."""
        content = "- <text>teh cat</text> Spelling error: 'teh' should be 'the'"
        result = extract_annotated_errors(content)
        assert len(result) == 1
        assert result[0] == ("teh cat", "Spelling error: 'teh' should be 'the'")
    
    def test_extract_annotated_errors_multiple(self):
        """Test extraction of multiple errors."""
        content = """- <text>I goes</text> Subject-verb disagreement
        - <text>very good</text> Use 'very well' instead"""
        result = extract_annotated_errors(content)
        assert len(result) == 2
        assert result[0] == ("I goes", "Subject-verb disagreement")
        assert result[1] == ("very good", "Use 'very well' instead")
    
    def test_extract_annotated_errors_empty(self):
        """Test extraction with empty content."""
        result = extract_annotated_errors("")
        assert result == []
    
    def test_extract_annotated_errors_none(self):
        """Test extraction with 'None.' content."""
        result = extract_annotated_errors("None.")
        assert result == []
    
    def test_extract_annotated_errors_complex_explanation(self):
        """Test extraction with complex explanations."""
        content = """- <text>I can to speak</text> Remove 'to' - use 'I can speak' 
        Modal verbs are followed by bare infinitive"""
        result = extract_annotated_errors(content)
        assert len(result) == 1
        assert result[0][0] == "I can to speak"
        assert "Remove 'to'" in result[0][1]
        assert "Modal verbs" in result[0][1]
    
    def test_extract_annotated_errors_no_text_tag(self):
        """Test extraction when explanation applies to whole text."""
        content = "- <text></text> Overall structure needs improvement"
        result = extract_annotated_errors(content)
        assert len(result) == 1
        assert result[0] == ("", "Overall structure needs improvement")


class TestFormatMistakesList:
    """Tests for formatting mistakes for display."""
    
    def test_format_mistakes_list_empty(self):
        """Test formatting empty mistakes list."""
        result = format_mistakes_list([])
        assert result == "No grammatical mistakes found."
    
    def test_format_mistakes_list_single(self):
        """Test formatting single mistake."""
        mistakes = [("teh cat", "Spelling error")]
        result = format_mistakes_list(mistakes)
        assert result == "- teh cat: Spelling error"
    
    def test_format_mistakes_list_multiple(self):
        """Test formatting multiple mistakes."""
        mistakes = [
            ("I goes", "Subject-verb agreement"),
            ("very good", "Use adverb 'well'")
        ]
        result = format_mistakes_list(mistakes)
        lines = result.split('\n')
        assert len(lines) == 2
        assert "- I goes: Subject-verb agreement" in lines
        assert "- very good: Use adverb 'well'" in lines
    
    def test_format_mistakes_list_empty_text(self):
        """Test formatting mistake with empty text (general feedback)."""
        mistakes = [("", "Overall structure issue")]
        result = format_mistakes_list(mistakes)
        assert result == "- Overall structure issue"


def create_mock_response(content: str):
    """Helper to create mock LLM response structure."""
    @dataclass
    class MockMessage:
        content: str
    
    @dataclass
    class MockChoice:
        message: MockMessage
    
    @dataclass
    class MockResponse:
        choices: list
    
    return MockResponse(choices=[MockChoice(message=MockMessage(content=content))])


@pytest.fixture
def sample_definitions():
    """Sample exercise definitions for testing."""
    return {
        "Essay": {
            "expected_length": [100, 200],
            "requirements": "Write a structured essay with introduction, body, and conclusion"
        },
        "Letter": {
            "expected_length": [50, 100],
            "requirements": "Write a formal or informal letter"
        }
    }


class TestExerciseGeneration:
    """Tests for exercise generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_exercise_success(self, sample_definitions):
        """Test successful exercise generation."""
        # Mock LLM response
        response_content = """<exercise>Write about your favorite hobby</exercise>
        <hints>Use present tense. Include specific details.</hints>"""
        
        mock_response = create_mock_response(response_content)
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.02))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        exercise_text, hints, cost = await generate_exercise(
            "English", "B1", "Essay", sample_definitions, llm_provider=llm_provider
        )
        
        assert exercise_text == "Write about your favorite hobby"
        assert "Use present tense" in hints
        assert cost == 0.02
        mock_llm.completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_exercise_no_hints(self, sample_definitions):
        """Test exercise generation with no hints."""
        response_content = """<exercise>Describe your hometown</exercise>
        <hints>None.</hints>"""
        
        mock_response = create_mock_response(response_content)
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.01))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        exercise_text, hints, cost = await generate_exercise(
            "Polish", "A2", "Letter", sample_definitions, llm_provider=llm_provider
        )
        
        assert exercise_text == "Describe your hometown"
        assert hints == ""  # Should be empty when "None."
    
    @pytest.mark.asyncio
    async def test_generate_custom_hints(self):
        """Test custom hints generation."""
        response_content = """<hints>Focus on descriptive language. Use past tense for actions.</hints>"""
        
        mock_response = create_mock_response(response_content)
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.015))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        hints, cost = await generate_custom_hints(
            "Spanish", "B2", "Write about a memorable vacation", llm_provider=llm_provider
        )
        
        assert "descriptive language" in hints
        assert "past tense" in hints
        assert cost == 0.015
    
    @patch('language_tutor.exercise.logger')
    @pytest.mark.asyncio
    async def test_generate_exercise_logging(self, mock_logger, sample_definitions):
        """Test that exercise generation logs appropriately."""
        response_content = """<exercise>Test exercise</exercise>
        <hints>Test hints</hints>"""
        
        mock_response = create_mock_response(response_content)
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.01))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        await generate_exercise("English", "B1", "Essay", sample_definitions, llm_provider=llm_provider)
        
        # Verify logging calls
        assert mock_logger.info.call_count >= 3  # Response, exercise, hints


class TestWritingCheck:
    """Tests for writing checking functionality."""
    
    @pytest.mark.asyncio
    async def test_check_writing_success(self, sample_definitions):
        """Test successful writing check."""
        feedback_content = """<mistakes>
        - <text>I goes</text> Subject-verb disagreement: use 'I go'
        - <text>very good</text> Use adverb: 'very well'
        </mistakes>
        
        <stylistic_errors>
        - <text>The text</text> Repetitive word usage
        </stylistic_errors>
        
        <recommendations>
        Use more varied vocabulary. Practice subject-verb agreement.
        </recommendations>"""
        
        mock_response = create_mock_response(feedback_content)
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.03))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        mistakes, style_errors, recommendations, cost = await check_writing(
            "English", "B1", "Write about hobbies", "I goes to gym very good", 
            "Essay", sample_definitions, llm_provider=llm_provider
        )
        
        assert len(mistakes) == 2
        assert mistakes[0] == ("I goes", "Subject-verb disagreement: use 'I go'")
        assert mistakes[1] == ("very good", "Use adverb: 'very well'")
        
        assert len(style_errors) == 1
        assert style_errors[0] == ("The text", "Repetitive word usage")
        
        assert "varied vocabulary" in recommendations
        assert cost == 0.03
    
    @pytest.mark.asyncio
    async def test_check_writing_no_errors(self, sample_definitions):
        """Test writing check with no errors found."""
        feedback_content = """<mistakes>
        None.
        </mistakes>
        
        <stylistic_errors>
        None.
        </stylistic_errors>
        
        <recommendations>
        Good work! Your writing is clear and grammatically correct.
        </recommendations>"""
        
        mock_response = create_mock_response(feedback_content)
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.02))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        mistakes, style_errors, recommendations, cost = await check_writing(
            "English", "C1", "Excellent essay", "This is well-written text.", 
            "Essay", sample_definitions, llm_provider=llm_provider
        )
        
        assert len(mistakes) == 0
        assert len(style_errors) == 0
        assert "Good work" in recommendations
    
    @patch('language_tutor.exercise.logger')
    @pytest.mark.asyncio
    async def test_check_writing_logging(self, mock_logger, sample_definitions):
        """Test that writing check logs feedback and results."""
        feedback_content = """<mistakes>None.</mistakes>
        <stylistic_errors>None.</stylistic_errors>
        <recommendations>Keep practicing!</recommendations>"""
        
        mock_response = create_mock_response(feedback_content)
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.01))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        await check_writing("English", "A1", "Test", "Text", "Essay", sample_definitions, llm_provider=llm_provider)
        
        # Verify logging calls for feedback response and parsed results
        assert mock_logger.info.call_count >= 4


class TestPromptConstruction:
    """Tests for prompt construction in exercise functions."""
    
    @patch('language_tutor.exercise.random.randint')
    @pytest.mark.asyncio
    async def test_generate_exercise_prompt_includes_requirements(self, mock_randint, sample_definitions):
        """Test that exercise generation prompt includes definition requirements."""
        mock_randint.return_value = 1234
        
        mock_response = create_mock_response("<exercise>Test</exercise><hints>None.</hints>")
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.01))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        await generate_exercise("English", "B1", "Essay", sample_definitions, llm_provider=llm_provider)
        
        # Check that the prompt included the requirements
        call_args = mock_llm.completion.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        assert "English" in prompt
        assert "B1" in prompt
        assert "Essay" in prompt
        assert sample_definitions["Essay"]["requirements"] in prompt
        assert "100" in prompt and "200" in prompt  # Expected length
        assert "1234" in prompt  # Random number
    
    @pytest.mark.asyncio
    async def test_check_writing_prompt_construction(self, sample_definitions):
        """Test that writing check prompt is properly constructed."""
        mock_response = create_mock_response("<mistakes>None.</mistakes><stylistic_errors>None.</stylistic_errors><recommendations>Good.</recommendations>")
        mock_llm = Mock(spec=LLM)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.01))
        
        # Create provider with mock LLM
        llm_provider = create_provider(mock_llm)
        
        await check_writing(
            "Spanish", "A2", "Describe your family", "Mi familia es grande", 
            "Description", sample_definitions, llm_provider=llm_provider
        )
        
        call_args = mock_llm.completion.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        assert "Spanish" in prompt
        assert "A2" in prompt
        assert "Describe your family" in prompt
        assert "Mi familia es grande" in prompt
        assert "Description" in prompt