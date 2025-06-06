"""Tests for question answering functionality."""

import pytest
from unittest.mock import patch, AsyncMock
from dataclasses import dataclass

from language_tutor.qa import answer_question


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


class TestAnswerQuestion:
    """Tests for the answer_question function."""
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_basic(self, mock_llm):
        """Test basic question answering functionality."""
        mock_response = create_mock_response("The present tense of 'to be' is 'am', 'is', or 'are'.")
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.015))
        
        context = {
            'language': 'English',
            'level': 'A1',
            'exercise_type': 'Grammar',
            'exercise': 'Practice using the verb "to be"'
        }
        
        answer, cost = await answer_question(
            "gpt-3.5-turbo",
            "What is the present tense of 'to be'?",
            context
        )
        
        assert "present tense" in answer
        assert "'to be'" in answer
        assert cost == 0.015
        mock_llm.completion.assert_called_once()
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_prompt_construction(self, mock_llm):
        """Test that the prompt is properly constructed with context."""
        mock_response = create_mock_response("Test response")
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.01))
        
        context = {
            'language': 'Spanish',
            'level': 'B2',
            'exercise_type': 'Essay',
            'exercise': 'Write about your hometown'
        }
        
        await answer_question(
            "claude-3-opus",
            "How do I use subjunctive mood?",
            context
        )
        
        # Check the call arguments
        call_args = mock_llm.completion.call_args
        messages = call_args[1]['messages']
        prompt = messages[0]['content']
        
        # Verify context is included in prompt
        assert 'Spanish' in prompt
        assert 'B2' in prompt
        assert 'Essay' in prompt
        assert 'Write about your hometown' in prompt
        assert 'How do I use subjunctive mood?' in prompt
        assert 'language learning assistant' in prompt
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_with_different_models(self, mock_llm):
        """Test question answering with different AI models."""
        mock_response = create_mock_response("Model-specific response")
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.02))
        
        context = {
            'language': 'French',
            'level': 'C1',
            'exercise_type': 'Translation',
            'exercise': 'Translate complex sentences'
        }
        
        models_to_test = [
            "openrouter/google/gemini-2.5-flash-preview-05-20",
            "openrouter/anthropic/claude-3-opus",
            "openrouter/openai/gpt-4o"
        ]
        
        for model in models_to_test:
            answer, cost = await answer_question(
                model,
                "What's the difference between passé composé and imparfait?",
                context
            )
            
            assert answer == "Model-specific response"
            assert cost == 0.02
            
            # Check model was passed correctly
            call_args = mock_llm.completion.call_args
            assert call_args[1]['model'] == model
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_complex_context(self, mock_llm):
        """Test question answering with complex context information."""
        mock_response = create_mock_response("Detailed grammatical explanation")
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.025))
        
        context = {
            'language': 'German',
            'level': 'A2',
            'exercise_type': 'Dialogue',
            'exercise': 'Create a conversation between two friends planning a vacation'
        }
        
        question = "When should I use 'der', 'die', or 'das'?"
        
        answer, cost = await answer_question("test-model", question, context)
        
        # Verify response
        assert answer == "Detailed grammatical explanation"
        assert cost == 0.025
        
        # Verify prompt includes all context
        call_args = mock_llm.completion.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        assert 'German' in prompt
        assert 'A2' in prompt
        assert 'Dialogue' in prompt
        assert 'conversation between two friends' in prompt
        assert 'planning a vacation' in prompt
        assert question in prompt
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_educational_focus(self, mock_llm):
        """Test that the prompt emphasizes educational focus."""
        mock_response = create_mock_response("Educational response")
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.01))
        
        context = {
            'language': 'Italian',
            'level': 'B1',
            'exercise_type': 'Reading',
            'exercise': 'Read and analyze a short story'
        }
        
        await answer_question(
            "test-model",
            "What does this word mean?",
            context
        )
        
        call_args = mock_llm.completion.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        # Check educational focus keywords
        assert 'helpful' in prompt.lower()
        assert 'educational' in prompt.lower()
        assert 'language learning' in prompt.lower()
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_response_extraction(self, mock_llm):
        """Test that response content is correctly extracted."""
        expected_answer = "This is a detailed explanation about grammar rules."
        mock_response = create_mock_response(expected_answer)
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.018))
        
        context = {
            'language': 'Portuguese',
            'level': 'C2',
            'exercise_type': 'Advanced Writing',
            'exercise': 'Write a formal business proposal'
        }
        
        answer, cost = await answer_question(
            "advanced-model",
            "How do I maintain formal tone?",
            context
        )
        
        assert answer == expected_answer
        assert cost == 0.018
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_error_handling(self, mock_llm):
        """Test error handling when LLM call fails."""
        # Mock an exception from the LLM
        mock_llm.completion = AsyncMock(side_effect=Exception("API Error"))
        
        context = {
            'language': 'English',
            'level': 'A1',
            'exercise_type': 'Basic',
            'exercise': 'Simple exercise'
        }
        
        with pytest.raises(Exception, match="API Error"):
            await answer_question("model", "Test question", context)
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_answer_question_empty_response(self, mock_llm):
        """Test handling of empty response from LLM."""
        mock_response = create_mock_response("")
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.001))
        
        context = {
            'language': 'English',
            'level': 'A1',
            'exercise_type': 'Test',
            'exercise': 'Test exercise'
        }
        
        answer, cost = await answer_question("model", "Test?", context)
        
        assert answer == ""
        assert cost == 0.001


class TestQAIntegration:
    """Integration tests for Q&A functionality."""
    
    @patch('language_tutor.qa.llm')
    @pytest.mark.asyncio
    async def test_qa_full_workflow(self, mock_llm):
        """Test a complete Q&A workflow."""
        mock_response = create_mock_response(
            "In Spanish, subjunctive mood is used to express doubt, emotion, or hypothetical situations. "
            "For example: 'Espero que tengas un buen día' (I hope you have a good day)."
        )
        mock_llm.completion = AsyncMock(return_value=(mock_response, 0.03))
        
        # Simulate a realistic Q&A scenario
        context = {
            'language': 'Spanish',
            'level': 'B1',
            'exercise_type': 'Conditional Sentences',
            'exercise': 'Write sentences expressing wishes and hypothetical situations'
        }
        
        question = "When do I use subjunctive mood in Spanish?"
        
        answer, cost = await answer_question(
            "openrouter/anthropic/claude-3-opus",
            question,
            context
        )
        
        # Verify educational quality of response
        assert "subjunctive" in answer.lower()
        assert "spanish" in answer.lower()
        assert "example" in answer.lower()
        assert cost > 0
        
        # Verify proper API usage
        mock_llm.completion.assert_called_once()
        call_args = mock_llm.completion.call_args
        
        # Check model parameter
        assert call_args[1]['model'] == "openrouter/anthropic/claude-3-opus"
        
        # Check messages structure
        messages = call_args[1]['messages']
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        assert 'content' in messages[0]