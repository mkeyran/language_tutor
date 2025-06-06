from .polish import (
    EXERCISE_DEFINITIONS as POLISH_EXERCISE_DEFINITIONS,
    EXERCISE_TYPES as POLISH_EXERCISE_TYPES,
)
from .portuguese import (
    EXERCISE_DEFINITIONS as PORTUGUESE_EXERCISE_DEFINITIONS,
    EXERCISE_TYPES as PORTUGUESE_EXERCISE_TYPES,
)
from .english import (
    EXERCISE_DEFINITIONS as ENGLISH_EXERCISE_DEFINITIONS,
    EXERCISE_TYPES as ENGLISH_EXERCISE_TYPES,
)

definitions = {
    "pl": POLISH_EXERCISE_DEFINITIONS,
    "pt": PORTUGUESE_EXERCISE_DEFINITIONS,
    "en": ENGLISH_EXERCISE_DEFINITIONS,
}

exercise_types = {
    "pl": POLISH_EXERCISE_TYPES,
    "pt": PORTUGUESE_EXERCISE_TYPES,
    "en": ENGLISH_EXERCISE_TYPES,
}

for type in exercise_types.keys():
    exercise_types[type] = (
        [("Random", "Random")] + exercise_types[type] + [("Custom", "Custom")]
    )


def get_language_data():
    """Get exercise types and definitions for all languages."""
    return exercise_types, definitions
