"""Tests for OpenAI LLM implementation."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from language_tutor.llms.openai_impl import OpenAILLM


class TestOpenAILLM:
    """Tests for OpenAI LLM implementation."""

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_with_env_vars(self):
        """Test OpenAI LLM initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test_openai_key",
                "OPENAI_BASE_URL": "https://custom.openai.com",
            },
        ):
            llm_instance = OpenAILLM()
            assert llm_instance.get_api_key() == "test_openai_key"
            assert llm_instance.get_base_url() == "https://custom.openai.com"

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_env_vars(self):
        """Test OpenAI LLM initialization without environment variables."""
        llm_instance = OpenAILLM()
        assert llm_instance.get_api_key() == ""
        assert llm_instance.get_base_url() == OpenAILLM.DEFAULT_BASE_URL

    def test_set_api_key(self):
        """Test setting API key."""
        llm_instance = OpenAILLM()
        llm_instance.set_api_key("new_openai_key")
        assert llm_instance.get_api_key() == "new_openai_key"
        assert os.environ.get("OPENAI_API_KEY") == "new_openai_key"

    def test_get_api_key(self):
        """Test getting API key."""
        llm_instance = OpenAILLM()
        llm_instance._api_key = "retrieved_key"
        assert llm_instance.get_api_key() == "retrieved_key"

    def test_is_configured_true(self):
        """Test is_configured returns True when API key is set."""
        llm_instance = OpenAILLM()
        llm_instance._api_key = "some_key"
        assert llm_instance.is_configured() is True

    def test_is_configured_false(self):
        """Test is_configured returns False when API key is not set."""
        llm_instance = OpenAILLM()
        llm_instance._api_key = ""
        assert llm_instance.is_configured() is False

    def test_set_base_url(self):
        """Test setting base URL."""
        llm_instance = OpenAILLM()
        llm_instance.set_base_url("https://new.openai.com")
        assert llm_instance.get_base_url() == "https://new.openai.com"
        assert os.environ.get("OPENAI_BASE_URL") == "https://new.openai.com"

    def test_get_base_url(self):
        """Test getting base URL."""
        llm_instance = OpenAILLM()
        llm_instance._base_url = "https://current.openai.com"
        assert llm_instance.get_base_url() == "https://current.openai.com"

    @pytest.mark.asyncio
    async def test_completion_success(self):
        """Test successful completion call."""
        # Mock the response
        mock_response = Mock()
        mock_openai = Mock()
        mock_openai.ChatCompletion.acreate = AsyncMock(return_value=mock_response)

        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_openai if name == 'openai' else __import__(name, *args, **kwargs)):
            llm_instance = OpenAILLM()
            llm_instance._api_key = "test_key"

            messages = [{"role": "user", "content": "Test message"}]
            response, cost = await llm_instance.completion("gpt-3.5-turbo", messages)

            assert response is mock_response
            assert cost is None  # OpenAI implementation doesn't calculate cost

            mock_openai.ChatCompletion.acreate.assert_called_once_with(
                model="gpt-3.5-turbo", messages=messages
            )
            assert mock_openai.api_key == "test_key"

    @pytest.mark.asyncio
    async def test_completion_with_kwargs(self):
        """Test completion with additional kwargs."""
        mock_response = Mock()
        mock_openai = Mock()
        mock_openai.ChatCompletion.acreate = AsyncMock(return_value=mock_response)

        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_openai if name == 'openai' else __import__(name, *args, **kwargs)):
            llm_instance = OpenAILLM()
            llm_instance._api_key = "test_key"
            llm_instance._base_url = "https://test.openai.com"

            messages = [{"role": "user", "content": "Test"}]

            await llm_instance.completion(
                "gpt-4", messages, temperature=0.8, max_tokens=150
            )

            mock_openai.ChatCompletion.acreate.assert_called_once_with(
                model="gpt-4", messages=messages, temperature=0.8, max_tokens=150
            )

    @pytest.mark.asyncio
    async def test_completion_sets_api_base_when_available(self):
        """Test that api_base is set when the attribute exists."""
        mock_response = Mock()
        mock_openai = Mock()
        mock_openai.api_base = None  # Simulate the attribute existing
        mock_openai.ChatCompletion.acreate = AsyncMock(return_value=mock_response)

        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_openai if name == 'openai' else __import__(name, *args, **kwargs)):
            llm_instance = OpenAILLM()
            llm_instance._api_key = "test_key"
            llm_instance._base_url = "https://custom.openai.com"

            messages = [{"role": "user", "content": "Test"}]
            await llm_instance.completion("gpt-3.5-turbo", messages)

            assert mock_openai.api_base == "https://custom.openai.com"

    @pytest.mark.asyncio
    async def test_completion_import_error(self):
        """Test completion raises error when openai library not available."""
        llm_instance = OpenAILLM()

        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'openai'")
        ):
            with pytest.raises(RuntimeError, match="openai library is required"):
                await llm_instance.completion("gpt-3.5-turbo", [])

    @pytest.mark.asyncio
    async def test_completion_handles_openai_exception(self):
        """Test that OpenAI exceptions are propagated."""
        mock_openai = Mock()
        mock_openai.ChatCompletion.acreate = AsyncMock(
            side_effect=Exception("OpenAI API Error")
        )

        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_openai if name == 'openai' else __import__(name, *args, **kwargs)):
            llm_instance = OpenAILLM()
            llm_instance._api_key = "test_key"

            with pytest.raises(Exception, match="OpenAI API Error"):
                await llm_instance.completion("gpt-3.5-turbo", [])


class TestOpenAILLMIntegration:
    """Integration tests for OpenAI LLM."""

    def test_environment_variable_handling(self):
        """Test proper handling of environment variables."""
        original_key = os.environ.get("OPENAI_API_KEY")
        original_url = os.environ.get("OPENAI_BASE_URL")

        try:
            # Clear environment
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("OPENAI_BASE_URL", None)

            # Test with empty environment
            llm = OpenAILLM()
            assert llm.get_api_key() == ""
            assert llm.get_base_url() == OpenAILLM.DEFAULT_BASE_URL
            assert not llm.is_configured()

            # Set through methods
            llm.set_api_key("method_key")
            llm.set_base_url("https://method.url.com")

            assert llm.get_api_key() == "method_key"
            assert llm.get_base_url() == "https://method.url.com"
            assert llm.is_configured()

            # Check environment was updated
            assert os.environ.get("OPENAI_API_KEY") == "method_key"
            assert os.environ.get("OPENAI_BASE_URL") == "https://method.url.com"

        finally:
            # Restore original environment
            if original_key is not None:
                os.environ["OPENAI_API_KEY"] = original_key
            else:
                os.environ.pop("OPENAI_API_KEY", None)

            if original_url is not None:
                os.environ["OPENAI_BASE_URL"] = original_url
            else:
                os.environ.pop("OPENAI_BASE_URL", None)
