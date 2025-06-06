"""Comprehensive tests for LLM integration layer."""

import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass

from language_tutor.llm import get_llm, set_llm
from language_tutor.llms.base import LLM
from language_tutor.llms.lite import LiteLLM


class MockLLM(LLM):
    """Mock LLM implementation for testing."""
    
    def __init__(self):
        self._api_key = ""
        self._base_url = "https://test.api.com"
        
    def set_api_key(self, key: str) -> None:
        self._api_key = key
        
    def get_api_key(self) -> str:
        return self._api_key
        
    def is_configured(self) -> bool:
        return bool(self._api_key)
        
    def set_base_url(self, url: str) -> None:
        self._base_url = url
        
    def get_base_url(self) -> str:
        return self._base_url
        
    async def completion(self, model: str, messages: list, **kwargs):
        # Mock response structure
        @dataclass
        class MockChoice:
            message: object
            
        @dataclass  
        class MockMessage:
            content: str = "Mock response"
            
        @dataclass
        class MockResponse:
            choices: list
            
        return MockResponse(choices=[MockChoice(message=MockMessage())]), 0.01


class TestLLMInterface:
    """Tests for the main LLM interface module."""
    
    def test_default_llm_instance(self):
        """Test that default LLM instance is LiteLLM."""
        current_llm = get_llm()
        assert isinstance(current_llm, LiteLLM)
    
    def test_set_llm_changes_global_instance(self):
        """Test that set_llm changes the global LLM instance."""
        original_llm = get_llm()
        mock_llm = MockLLM()
        
        try:
            set_llm(mock_llm)
            assert get_llm() is mock_llm
            assert get_llm() is not original_llm
        finally:
            # Restore original LLM
            set_llm(original_llm)
    
    def test_get_llm_returns_current_instance(self):
        """Test that get_llm returns the currently configured instance."""
        mock_llm = MockLLM()
        original_llm = get_llm()
        
        try:
            set_llm(mock_llm)
            current = get_llm()
            assert current is mock_llm
        finally:
            set_llm(original_llm)


class TestLiteLLM:
    """Tests for LiteLLM implementation."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_with_env_vars(self):
        """Test LiteLLM initialization with environment variables."""
        mock_litellm = Mock()
        mock_litellm.api_key = None
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        
        with patch.dict(os.environ, {
            'OPENROUTER_API_KEY': 'test_key',
            'OPENROUTER_BASE_URL': 'https://custom.api.com'
        }):
            with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                       mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
                llm_instance = LiteLLM()
                assert llm_instance._litellm.api_key == 'test_key'
                assert llm_instance._litellm.base_url == 'https://custom.api.com'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_env_vars(self):
        """Test LiteLLM initialization without environment variables."""
        mock_litellm = Mock()
        mock_litellm.api_key = None
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
            llm_instance = LiteLLM()
            assert llm_instance._litellm.base_url == LiteLLM.DEFAULT_BASE_URL
    
    def test_set_api_key(self):
        """Test setting API key."""
        original_api_key = os.environ.get("OPENROUTER_API_KEY")
        
        try:
            mock_litellm = Mock()
            mock_litellm.api_key = None
            mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
            
            with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                       mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
                llm_instance = LiteLLM()
                llm_instance.set_api_key("new_test_key")
                assert llm_instance._litellm.api_key == "new_test_key"
                assert os.environ.get("OPENROUTER_API_KEY") == "new_test_key"
        finally:
            # Clean up environment
            if original_api_key is not None:
                os.environ["OPENROUTER_API_KEY"] = original_api_key
            else:
                os.environ.pop("OPENROUTER_API_KEY", None)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key(self):
        """Test getting API key."""
        mock_litellm = Mock()
        mock_litellm.api_key = "retrieved_key"
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
            llm_instance = LiteLLM()
            assert llm_instance.get_api_key() == "retrieved_key"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_empty(self):
        """Test getting API key when None."""
        mock_litellm = Mock()
        mock_litellm.api_key = None
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
            llm_instance = LiteLLM()
            assert llm_instance.get_api_key() == ""
    
    def test_is_configured_true(self):
        """Test is_configured returns True when API key is set."""
        mock_litellm = Mock()
        mock_litellm.api_key = "some_key"
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
            llm_instance = LiteLLM()
            assert llm_instance.is_configured() is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_is_configured_false(self):
        """Test is_configured returns False when API key is not set."""
        mock_litellm = Mock()
        mock_litellm.api_key = None
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
            llm_instance = LiteLLM()
            assert llm_instance.is_configured() is False
    
    def test_set_base_url(self):
        """Test setting base URL."""
        original_base_url = os.environ.get("OPENROUTER_BASE_URL")
        
        try:
            mock_litellm = Mock()
            mock_litellm.api_key = None
            mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
            
            with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                       mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
                llm_instance = LiteLLM()
                llm_instance.set_base_url("https://new.api.com")
                assert llm_instance._litellm.base_url == "https://new.api.com"
                assert os.environ.get("OPENROUTER_BASE_URL") == "https://new.api.com"
        finally:
            # Clean up environment
            if original_base_url is not None:
                os.environ["OPENROUTER_BASE_URL"] = original_base_url
            else:
                os.environ.pop("OPENROUTER_BASE_URL", None)
    
    def test_get_base_url(self):
        """Test getting base URL."""
        original_base_url = os.environ.get("OPENROUTER_BASE_URL")
        
        try:
            # Clear environment first
            os.environ.pop("OPENROUTER_BASE_URL", None)
            
            mock_litellm = Mock()
            mock_litellm.api_key = None
            mock_litellm.base_url = "https://current.api.com"
            
            with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                       mock_litellm if name == 'litellm' else __import__(name, *args, **kwargs)):
                llm_instance = LiteLLM()
                # Manually set the base_url since our mock setup overrides the default
                llm_instance._litellm.base_url = "https://current.api.com"
                assert llm_instance.get_base_url() == "https://current.api.com"
        finally:
            # Restore environment
            if original_base_url is not None:
                os.environ["OPENROUTER_BASE_URL"] = original_base_url
    
    @pytest.mark.asyncio
    async def test_completion_with_cost(self):
        """Test completion method with cost calculation."""
        # Mock response structure
        @dataclass
        class MockChoice:
            message: object
            
        @dataclass
        class MockMessage:
            content: str = "Test response"
            
        @dataclass
        class MockResponse:
            choices: list
            
        mock_response = MockResponse(choices=[MockChoice(message=MockMessage())])
        
        mock_litellm = Mock()
        mock_litellm.api_key = "test_key"
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        mock_litellm.acompletion = AsyncMock(return_value=mock_response)
        
        # Mock completion_cost as an importable module
        mock_completion_cost = Mock(return_value=0.05)
        
        def mock_import(name, *args, **kwargs):
            if name == 'litellm':
                # Add completion_cost to the mock module
                mock_litellm.completion_cost = mock_completion_cost
                return mock_litellm
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            llm_instance = LiteLLM()
            
            messages = [{"role": "user", "content": "Test message"}]
            
            response, cost = await llm_instance.completion(
                model="openrouter/google/gemini-2.5-flash-preview-05-20",
                messages=messages
            )
            
            assert response is mock_response
            assert cost == 0.05
            mock_litellm.acompletion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_completion_without_cost_info(self):
        """Test completion method when no cost info is available."""
        @dataclass
        class MockChoice:
            message: object
            
        @dataclass
        class MockMessage:
            content: str = "Test response"
            
        @dataclass
        class MockResponse:
            choices: list
            
        mock_response = MockResponse(choices=[MockChoice(message=MockMessage())])
        
        mock_litellm = Mock()
        mock_litellm.api_key = "test_key"
        mock_litellm.base_url = LiteLLM.DEFAULT_BASE_URL
        mock_litellm.acompletion = AsyncMock(return_value=mock_response)
        
        # Mock completion_cost to simulate no cost info available
        mock_completion_cost = Mock(return_value=None)
        
        def mock_import(name, *args, **kwargs):
            if name == 'litellm':
                mock_litellm.completion_cost = mock_completion_cost
                return mock_litellm
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            llm_instance = LiteLLM()
            
            messages = [{"role": "user", "content": "Test message"}]
            
            response, cost = await llm_instance.completion(
                model="unknown/model",
                messages=messages
            )
            
            assert response is mock_response
            assert cost is None
            mock_litellm.acompletion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_completion_with_kwargs(self):
        """Test completion method passes through kwargs."""
        original_base_url = os.environ.get("OPENROUTER_BASE_URL")
        
        try:
            # Clear environment
            os.environ.pop("OPENROUTER_BASE_URL", None)
            
            @dataclass
            class MockChoice:
                message: object
                
            @dataclass
            class MockMessage:
                content: str = "Test response"
                
            @dataclass
            class MockResponse:
                choices: list
                
            mock_response = MockResponse(choices=[MockChoice(message=MockMessage())])
            
            mock_litellm = Mock()
            mock_litellm.api_key = "test_key"
            mock_litellm.base_url = "https://test.api.com"
            mock_litellm.acompletion = AsyncMock(return_value=mock_response)
            
            # Mock completion_cost
            mock_completion_cost = Mock(return_value=None)
            
            def mock_import(name, *args, **kwargs):
                if name == 'litellm':
                    mock_litellm.completion_cost = mock_completion_cost
                    return mock_litellm
                return __import__(name, *args, **kwargs)
            
            with patch('builtins.__import__', side_effect=mock_import):
                llm_instance = LiteLLM()
                # Manually set the base_url to the test value
                llm_instance._litellm.base_url = "https://test.api.com"
                
                messages = [{"role": "user", "content": "Test"}]
                
                await llm_instance.completion(
                    model="test/model",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=100
                )
                
                mock_litellm.acompletion.assert_called_once_with(
                    model="test/model",
                    messages=messages,
                    api_base="https://test.api.com",
                    temperature=0.7,
                    max_tokens=100
                )
        finally:
            # Restore environment
            if original_base_url is not None:
                os.environ["OPENROUTER_BASE_URL"] = original_base_url


class TestLLMBaseInterface:
    """Tests for LLM base class interface compliance."""
    
    def test_mock_llm_implements_interface(self):
        """Test that MockLLM properly implements the LLM interface."""
        mock_llm = MockLLM()
        
        # Test all required methods exist and work
        assert hasattr(mock_llm, 'set_api_key')
        assert hasattr(mock_llm, 'get_api_key')
        assert hasattr(mock_llm, 'is_configured')
        assert hasattr(mock_llm, 'set_base_url')
        assert hasattr(mock_llm, 'get_base_url')
        assert hasattr(mock_llm, 'completion')
        
        # Test basic functionality
        mock_llm.set_api_key("test")
        assert mock_llm.get_api_key() == "test"
        assert mock_llm.is_configured() is True
        
        mock_llm.set_base_url("https://test.com")
        assert mock_llm.get_base_url() == "https://test.com"
    
    @pytest.mark.asyncio
    async def test_mock_llm_completion(self):
        """Test MockLLM completion method."""
        mock_llm = MockLLM()
        messages = [{"role": "user", "content": "test"}]
        
        response, cost = await mock_llm.completion("test-model", messages)
        
        assert response is not None
        assert hasattr(response, 'choices')
        assert len(response.choices) > 0
        assert response.choices[0].message.content == "Mock response"
        assert cost == 0.01


class TestLLMIntegration:
    """Integration tests for LLM functionality."""
    
    @pytest.mark.asyncio
    async def test_llm_switching(self):
        """Test switching between different LLM implementations."""
        original_llm = get_llm()
        mock_llm = MockLLM()
        
        try:
            # Switch to mock LLM
            set_llm(mock_llm)
            current_llm = get_llm()
            assert current_llm is mock_llm
            
            # Test completion works with new LLM
            messages = [{"role": "user", "content": "test"}]
            response, cost = await current_llm.completion("test-model", messages)
            assert response.choices[0].message.content == "Mock response"
            
        finally:
            # Restore original LLM
            set_llm(original_llm)
    
    def test_llm_configuration_persistence(self):
        """Test that LLM configuration persists after switching."""
        original_llm = get_llm()
        mock_llm = MockLLM()
        
        try:
            # Configure mock LLM
            mock_llm.set_api_key("test_key")
            mock_llm.set_base_url("https://test.com")
            
            # Switch to mock LLM
            set_llm(mock_llm)
            current_llm = get_llm()
            
            # Verify configuration persists
            assert current_llm.get_api_key() == "test_key"
            assert current_llm.get_base_url() == "https://test.com"
            assert current_llm.is_configured() is True
            
        finally:
            set_llm(original_llm)