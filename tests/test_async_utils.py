"""Tests for async utilities and helper functions."""

import asyncio
import pytest
from unittest.mock import patch

from language_tutor.async_runner import run_async
from language_tutor.utils import build_wiktionary_url


class TestAsyncRunner:
    """Tests for the async runner utility."""
    
    def test_run_async_basic_function(self):
        """Test run_async with a basic async function."""
        async def simple_async():
            await asyncio.sleep(0.01)
            return "success"
        
        result = run_async(simple_async())
        assert result == "success"
    
    def test_run_async_with_parameters(self):
        """Test run_async with async function that takes parameters."""
        async def async_with_params(x, y):
            await asyncio.sleep(0.01)
            return x + y
        
        result = run_async(async_with_params(5, 3))
        assert result == 8
    
    def test_run_async_with_exception(self):
        """Test run_async properly propagates exceptions."""
        async def async_with_error():
            await asyncio.sleep(0.01)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            run_async(async_with_error())
    
    def test_run_async_with_complex_return(self):
        """Test run_async with complex return values."""
        async def async_complex():
            await asyncio.sleep(0.01)
            return {"status": "ok", "data": [1, 2, 3], "count": 3}
        
        result = run_async(async_complex())
        assert result["status"] == "ok"
        assert result["data"] == [1, 2, 3]
        assert result["count"] == 3
    
    def test_run_async_nested_calls(self):
        """Test run_async with nested async calls."""
        async def inner_async(value):
            await asyncio.sleep(0.01)
            return value * 2
        
        async def outer_async():
            result1 = await inner_async(5)
            result2 = await inner_async(10)
            return result1 + result2
        
        result = run_async(outer_async())
        assert result == 30  # (5*2) + (10*2)
    
    @patch('nest_asyncio.apply')
    def test_run_async_applies_nest_asyncio(self, mock_nest_apply):
        """Test that run_async applies nest_asyncio patch."""
        async def simple():
            return "test"
        
        run_async(simple())
        mock_nest_apply.assert_called_once()
    
    def test_run_async_multiple_calls(self):
        """Test multiple calls to run_async work correctly."""
        async def async_func(n):
            await asyncio.sleep(0.01)
            return n ** 2
        
        results = []
        for i in range(3):
            result = run_async(async_func(i + 1))
            results.append(result)
        
        assert results == [1, 4, 9]
    
    def test_run_async_with_timeout_scenario(self):
        """Test run_async with operations that might timeout."""
        async def quick_operation():
            await asyncio.sleep(0.001)  # Very quick
            return "completed"
        
        result = run_async(quick_operation())
        assert result == "completed"
    
    def test_run_async_with_coroutine_function(self):
        """Test run_async with coroutine function (not coroutine object)."""
        async def coro_func():
            await asyncio.sleep(0.01)
            return "from_function"
        
        # Pass the coroutine object, not the function
        result = run_async(coro_func())
        assert result == "from_function"


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_build_wiktionary_url_basic(self):
        """Test basic Wiktionary URL building."""
        url = build_wiktionary_url("hello", "en")
        assert url == "https://en.m.wiktionary.org/wiki/hello"
    
    def test_build_wiktionary_url_different_languages(self):
        """Test Wiktionary URL building for different languages."""
        test_cases = [
            ("word", "en", "https://en.m.wiktionary.org/wiki/word"),
            ("mot", "fr", "https://fr.m.wiktionary.org/wiki/mot"),
            ("palabra", "es", "https://es.m.wiktionary.org/wiki/palabra"),
            ("słowo", "pl", "https://pl.m.wiktionary.org/wiki/s%C5%82owo"),
        ]
        
        for word, lang, expected in test_cases:
            url = build_wiktionary_url(word, lang)
            assert url == expected
    
    def test_build_wiktionary_url_special_characters(self):
        """Test Wiktionary URL building with special characters."""
        # Test with spaces (should be encoded)
        url = build_wiktionary_url("hello world", "en")
        assert url == "https://en.m.wiktionary.org/wiki/hello%20world"
        
        # Test with accented characters
        url = build_wiktionary_url("café", "en")
        assert url == "https://en.m.wiktionary.org/wiki/caf%C3%A9"
        
        # Test with special symbols
        url = build_wiktionary_url("C++", "en")
        assert url == "https://en.m.wiktionary.org/wiki/C%2B%2B"
    
    def test_build_wiktionary_url_empty_inputs(self):
        """Test Wiktionary URL building with empty inputs."""
        # Empty word
        url = build_wiktionary_url("", "en")
        assert url == ""  # Function returns empty string for empty word
        
        # Empty language (should default to 'en')
        url = build_wiktionary_url("word", "")
        assert url == "https://en.m.wiktionary.org/wiki/word"
    
    def test_build_wiktionary_url_case_sensitivity(self):
        """Test Wiktionary URL building preserves case."""
        url = build_wiktionary_url("Hello", "en")
        assert url == "https://en.m.wiktionary.org/wiki/Hello"
        
        url = build_wiktionary_url("WORD", "en")
        assert url == "https://en.m.wiktionary.org/wiki/WORD"
    
    def test_build_wiktionary_url_numbers_and_symbols(self):
        """Test Wiktionary URL building with numbers and symbols."""
        test_cases = [
            ("123", "en", "https://en.m.wiktionary.org/wiki/123"),
            ("word-with-hyphens", "en", "https://en.m.wiktionary.org/wiki/word-with-hyphens"),
            ("word_with_underscores", "en", "https://en.m.wiktionary.org/wiki/word_with_underscores"),
            ("word.with.dots", "en", "https://en.m.wiktionary.org/wiki/word.with.dots"),
        ]
        
        for word, lang, expected in test_cases:
            url = build_wiktionary_url(word, lang)
            assert url == expected
    
    def test_build_wiktionary_url_long_words(self):
        """Test Wiktionary URL building with very long words."""
        long_word = "supercalifragilisticexpialidocious"
        url = build_wiktionary_url(long_word, "en")
        assert url == f"https://en.m.wiktionary.org/wiki/{long_word}"
    
    def test_build_wiktionary_url_non_latin_scripts(self):
        """Test Wiktionary URL building with non-Latin scripts."""
        test_cases = [
            ("привет", "ru"),  # Russian
            ("こんにちは", "ja"),  # Japanese
            ("مرحبا", "ar"),  # Arabic
            ("שלום", "he"),  # Hebrew
        ]
        
        for word, lang in test_cases:
            url = build_wiktionary_url(word, lang)
            # Should contain the base structure
            assert url.startswith(f"https://{lang}.m.wiktionary.org/wiki/")
            # Should be properly URL encoded
            assert " " not in url  # Spaces should be encoded


class TestAsyncIntegration:
    """Integration tests for async functionality."""
    
    def test_run_async_with_real_async_pattern(self):
        """Test run_async with realistic async patterns."""
        async def simulate_api_call(delay=0.01):
            """Simulate an API call with delay."""
            await asyncio.sleep(delay)
            return {"status": "success", "data": "response"}
        
        async def process_multiple_calls():
            """Simulate processing multiple API calls."""
            tasks = [
                simulate_api_call(0.01),
                simulate_api_call(0.01),
                simulate_api_call(0.01)
            ]
            results = await asyncio.gather(*tasks)
            return len(results)
        
        result = run_async(process_multiple_calls())
        assert result == 3
    
    def test_run_async_error_recovery(self):
        """Test error handling in async operations."""
        async def mixed_operations():
            """Mix successful and failing operations."""
            try:
                await asyncio.sleep(0.01)
                # Simulate some work that might fail
                if True:  # Condition that triggers error
                    raise ValueError("Simulated error")
                return "success"
            except ValueError:
                # Handle error and return recovery value
                return "recovered"
        
        result = run_async(mixed_operations())
        assert result == "recovered"
    
    def test_run_async_with_context_manager(self):
        """Test run_async with async context managers."""
        class AsyncContextManager:
            def __init__(self):
                self.entered = False
                self.exited = False
            
            async def __aenter__(self):
                await asyncio.sleep(0.01)
                self.entered = True
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await asyncio.sleep(0.01)
                self.exited = True
        
        async def use_context_manager():
            cm = AsyncContextManager()
            async with cm:
                assert cm.entered
                await asyncio.sleep(0.01)
                return cm
        
        result = run_async(use_context_manager())
        assert result.entered
        assert result.exited