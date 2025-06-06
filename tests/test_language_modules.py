"""Tests for language module definitions and structure."""

import pytest

from language_tutor.languages import (
    definitions, exercise_types,
    ENGLISH_EXERCISE_DEFINITIONS, ENGLISH_EXERCISE_TYPES,
    POLISH_EXERCISE_DEFINITIONS, POLISH_EXERCISE_TYPES,
    PORTUGUESE_EXERCISE_DEFINITIONS, PORTUGUESE_EXERCISE_TYPES
)
from language_tutor.languages.english import EXERCISE_DEFINITIONS as EN_DEFS, EXERCISE_TYPES as EN_TYPES
from language_tutor.languages.polish import EXERCISE_DEFINITIONS as PL_DEFS, EXERCISE_TYPES as PL_TYPES
from language_tutor.languages.portuguese import EXERCISE_DEFINITIONS as PT_DEFS, EXERCISE_TYPES as PT_TYPES


class TestLanguageModuleStructure:
    """Tests for overall language module structure."""
    
    def test_definitions_dict_has_all_languages(self):
        """Test that definitions dict contains all supported languages."""
        assert "en" in definitions
        assert "pl" in definitions
        assert "pt" in definitions
    
    def test_exercise_types_dict_has_all_languages(self):
        """Test that exercise_types dict contains all supported languages."""
        assert "en" in exercise_types
        assert "pl" in exercise_types
        assert "pt" in exercise_types
    
    def test_definitions_reference_correct_modules(self):
        """Test that definitions dict references correct module definitions."""
        assert definitions["en"] is ENGLISH_EXERCISE_DEFINITIONS
        assert definitions["pl"] is POLISH_EXERCISE_DEFINITIONS
        assert definitions["pt"] is PORTUGUESE_EXERCISE_DEFINITIONS
    
    def test_exercise_types_include_random_and_custom(self):
        """Test that all language exercise types include Random and Custom options."""
        for lang_code, types in exercise_types.items():
            # Should have Random as first option
            assert types[0] == ("Random", "Random")
            # Should have Custom as last option
            assert types[-1] == ("Custom", "Custom")
            # Should have at least 3 items (Random + at least 1 real type + Custom)
            assert len(types) >= 3


class TestExerciseDefinitionStructure:
    """Tests for exercise definition structure and validity."""
    
    def test_all_exercise_definitions_have_required_fields(self):
        """Test that all exercise definitions have required fields."""
        required_fields = ["expected_length", "requirements"]
        
        for lang_code, lang_definitions in definitions.items():
            for exercise_name, definition in lang_definitions.items():
                assert isinstance(definition, dict), f"{lang_code}.{exercise_name} should be a dict"
                
                for field in required_fields:
                    assert field in definition, f"{lang_code}.{exercise_name} missing field: {field}"
    
    def test_expected_length_format(self):
        """Test that expected_length fields have correct format."""
        for lang_code, lang_definitions in definitions.items():
            for exercise_name, definition in lang_definitions.items():
                expected_length = definition["expected_length"]
                
                # Should be a list/tuple of exactly 2 numbers
                assert isinstance(expected_length, (list, tuple)), \
                    f"{lang_code}.{exercise_name}.expected_length should be list/tuple"
                assert len(expected_length) == 2, \
                    f"{lang_code}.{exercise_name}.expected_length should have 2 elements"
                
                min_length, max_length = expected_length
                assert isinstance(min_length, int), \
                    f"{lang_code}.{exercise_name}.expected_length[0] should be int"
                assert isinstance(max_length, int), \
                    f"{lang_code}.{exercise_name}.expected_length[1] should be int"
                assert min_length > 0, \
                    f"{lang_code}.{exercise_name}.expected_length[0] should be positive"
                assert max_length >= min_length, \
                    f"{lang_code}.{exercise_name}.expected_length[1] should be >= min_length"
    
    def test_requirements_are_strings(self):
        """Test that requirements fields are non-empty strings."""
        for lang_code, lang_definitions in definitions.items():
            for exercise_name, definition in lang_definitions.items():
                requirements = definition["requirements"]
                
                assert isinstance(requirements, str), \
                    f"{lang_code}.{exercise_name}.requirements should be string"
                assert len(requirements.strip()) > 0, \
                    f"{lang_code}.{exercise_name}.requirements should not be empty"


class TestExerciseTypeStructure:
    """Tests for exercise type structure and validity."""
    
    def test_exercise_types_are_tuples(self):
        """Test that exercise types are properly formatted tuples."""
        for lang_code in ["en", "pl", "pt"]:
            # Get original types (without Random/Custom additions)
            if lang_code == "en":
                original_types = EN_TYPES
            elif lang_code == "pl":
                original_types = PL_TYPES
            else:
                original_types = PT_TYPES
            
            for exercise_type in original_types:
                assert isinstance(exercise_type, tuple), \
                    f"{lang_code} exercise type should be tuple: {exercise_type}"
                assert len(exercise_type) == 2, \
                    f"{lang_code} exercise type should have 2 elements: {exercise_type}"
                
                display_name, internal_name = exercise_type
                assert isinstance(display_name, str), \
                    f"{lang_code} display name should be string: {display_name}"
                assert isinstance(internal_name, str), \
                    f"{lang_code} internal name should be string: {internal_name}"
                assert len(display_name.strip()) > 0, \
                    f"{lang_code} display name should not be empty: {display_name}"
                assert len(internal_name.strip()) > 0, \
                    f"{lang_code} internal name should not be empty: {internal_name}"
    
    def test_exercise_types_match_definitions(self):
        """Test that exercise types have corresponding definitions."""
        type_mappings = {
            "en": (EN_TYPES, EN_DEFS),
            "pl": (PL_TYPES, PL_DEFS),
            "pt": (PT_TYPES, PT_DEFS)
        }
        
        for lang_code, (types, defs) in type_mappings.items():
            for display_name, internal_name in types:
                assert internal_name in defs, \
                    f"{lang_code}: Exercise type '{internal_name}' has no definition"
    
    def test_definitions_have_corresponding_types(self):
        """Test that all definitions have corresponding exercise types."""
        type_mappings = {
            "en": (EN_TYPES, EN_DEFS),
            "pl": (PL_TYPES, PL_DEFS),
            "pt": (PT_TYPES, PT_DEFS)
        }
        
        for lang_code, (types, defs) in type_mappings.items():
            # Extract internal names from types
            type_names = {internal_name for _, internal_name in types}
            
            for definition_name in defs.keys():
                assert definition_name in type_names, \
                    f"{lang_code}: Definition '{definition_name}' has no corresponding type"


class TestEnglishLanguageModule:
    """Tests specific to English language module."""
    
    def test_english_has_common_exercise_types(self):
        """Test that English module has expected common exercise types."""
        type_names = {internal_name for _, internal_name in EN_TYPES}
        
        # These are common exercise types we expect to see
        expected_types = ["Essay", "Letter"]  # Add more based on actual implementation
        
        for expected_type in expected_types:
            if expected_type in EN_DEFS:  # Only check if it exists in definitions
                assert expected_type in type_names, f"English should have {expected_type} type"
    
    def test_english_definitions_quality(self):
        """Test quality of English exercise definitions."""
        for exercise_name, definition in EN_DEFS.items():
            requirements = definition["requirements"]
            
            # Requirements should be descriptive
            assert len(requirements) > 20, \
                f"English {exercise_name} requirements should be descriptive"
            
            # Expected length should be reasonable for English
            min_len, max_len = definition["expected_length"]
            assert min_len >= 10, f"English {exercise_name} min length should be >= 10"
            assert max_len <= 1000, f"English {exercise_name} max length should be <= 1000"


class TestPolishLanguageModule:
    """Tests specific to Polish language module."""
    
    def test_polish_definitions_quality(self):
        """Test quality of Polish exercise definitions."""
        for exercise_name, definition in PL_DEFS.items():
            requirements = definition["requirements"]
            
            # Requirements should be descriptive
            assert len(requirements) > 10, \
                f"Polish {exercise_name} requirements should be descriptive"
            
            # Expected length should be reasonable
            min_len, max_len = definition["expected_length"]
            assert min_len >= 5, f"Polish {exercise_name} min length should be >= 5"
            assert max_len <= 1000, f"Polish {exercise_name} max length should be <= 1000"


class TestPortugueseLanguageModule:
    """Tests specific to Portuguese language module."""
    
    def test_portuguese_definitions_quality(self):
        """Test quality of Portuguese exercise definitions."""
        for exercise_name, definition in PT_DEFS.items():
            requirements = definition["requirements"]
            
            # Requirements should be descriptive
            assert len(requirements) > 10, \
                f"Portuguese {exercise_name} requirements should be descriptive"
            
            # Expected length should be reasonable
            min_len, max_len = definition["expected_length"]
            assert min_len >= 5, f"Portuguese {exercise_name} min length should be >= 5"
            assert max_len <= 1000, f"Portuguese {exercise_name} max length should be <= 1000"


class TestLanguageModuleConsistency:
    """Tests for consistency across language modules."""
    
    def test_all_languages_have_similar_structure(self):
        """Test that all language modules follow similar patterns."""
        languages = ["en", "pl", "pt"]
        
        # All should have at least some exercise types
        for lang in languages:
            original_types = exercise_types[lang][1:-1]  # Exclude Random and Custom
            assert len(original_types) > 0, f"{lang} should have at least one exercise type"
    
    def test_exercise_complexity_progression(self):
        """Test that exercise types have reasonable complexity progression."""
        for lang_code, lang_definitions in definitions.items():
            lengths = []
            for definition in lang_definitions.values():
                min_len, max_len = definition["expected_length"]
                lengths.append((min_len, max_len))
            
            # Should have variety in expected lengths
            if len(lengths) > 1:
                min_lengths = [min_len for min_len, _ in lengths]
                max_lengths = [max_len for _, max_len in lengths]
                
                # Should have some variation (not all the same)
                assert len(set(min_lengths)) > 1 or len(set(max_lengths)) > 1, \
                    f"{lang_code} should have variety in exercise lengths"
    
    def test_no_duplicate_exercise_names(self):
        """Test that each language has unique exercise names."""
        for lang_code, lang_definitions in definitions.items():
            exercise_names = list(lang_definitions.keys())
            unique_names = set(exercise_names)
            
            assert len(exercise_names) == len(unique_names), \
                f"{lang_code} has duplicate exercise names: {exercise_names}"