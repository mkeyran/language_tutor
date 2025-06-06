"""Exercise-related utilities for Language Tutor."""

import re
import random
from language_tutor.llm import get_llm, LLMProvider
from language_tutor.llms import LLM
from language_tutor.config import OR_MODEL_NAME

# Set up logging to file
import logging

logging.basicConfig(
    filename="language_tutor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def extract_content_from_xml(text, tag_name, default=""):
    """Extract content from XML tags, handling potential parsing issues.

    Args:
        text (str): The text containing XML tags
        tag_name (str): The name of the XML tag to extract from
        default (str): Default value if tag is not found or empty

    Returns:
        str: The content inside the XML tags or default value
    """
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        content = match.group(1).strip()
        return content if content and content.lower() != "none." else default
    return default


async def generate_exercise(language, level, exercise_type, definitions, llm_provider: LLMProvider | None = None):
    """Generate a new language exercise using the specified LLM provider.

    Args:
        language (str): The language code (e.g., "pl" for Polish)
        level (str): The proficiency level (e.g., "A1")
        exercise_type (str): The type of exercise to generate
        definitions (dict): Dictionary containing exercise definitions
        llm_provider (LLMProvider, optional): LLM provider to use. Uses default if None.

    Returns:
        tuple: (exercise_text, hints, cost)
    """
    # Construct prompt asking for specific formatting
    prompt = f"""Create a short '{exercise_type}' writing exercise for a learner of {language} for a proficiency level {level}.
    The expected length of the writing should be between {definitions[exercise_type]["expected_length"][0]} and {definitions[exercise_type]["expected_length"][1]} words.
    Random number is {random.randint(1, 10000)} (don't use it, it is just to make the prompt different).
Provide the exercise text and optionally some hints. The requirements for the exercise are:
'{definitions[exercise_type]["requirements"]}'
You should generate exactly one exercise. It should be a task, not the text of the exercise itself.

Format the output EXACTLY like this, using these specific XML tags:

<exercise>
The exercise text goes here
</exercise>

<hints>
Optional hints go here. You can add useful phrases in addition to the hints. If no hints, write "None."
</hints>
Please use markdown for hints formatting.

"""
    messages = [{"role": "user", "content": prompt}]

    # Get LLM instance
    llm = llm_provider.get_llm() if llm_provider else get_llm()

    # Make the async API call
    response, cost = await llm.completion(model=OR_MODEL_NAME, messages=messages)

    full_response_content = response.choices[0].message.content

    # Log the response for debugging
    logger.info(f"Generated exercise response: {full_response_content}")
    # Parse XML output
    exercise_text = extract_content_from_xml(full_response_content, "exercise")
    hints = extract_content_from_xml(full_response_content, "hints", "")
    logger.info(f"Exercise text: {exercise_text}")
    logger.info(f"Hints: {hints}")

    return exercise_text, hints, cost


async def generate_custom_hints(language, level, exercise_text, llm_provider: LLMProvider | None = None):
    """Generate hints for a user-provided exercise text.

    Args:
        language (str): Target language code.
        level (str): Proficiency level of the learner.
        exercise_text (str): The custom exercise provided by the user.
        llm_provider (LLMProvider, optional): LLM provider to use. Uses default if None.

    Returns:
        tuple: (hints, cost)
    """
    prompt = f"""Provide helpful hints or useful phrases for the following {language} writing exercise aimed at level {level} learners:
{exercise_text}

Format the output EXACTLY like this using XML tags:
<hints>
Your hints here or \"None.\"
</hints>

Please use markdown for hints formatting.
"""

    messages = [{"role": "user", "content": prompt}]
    
    # Get LLM instance
    llm = llm_provider.get_llm() if llm_provider else get_llm()
    
    response, cost = await llm.completion(model=OR_MODEL_NAME, messages=messages)

    full_response_content = response.choices[0].message.content
    logger.info(f"Custom hints response: {full_response_content}")
    hints = extract_content_from_xml(full_response_content, "hints", "")
    logger.info(f"Custom hints: {hints}")

    return hints, cost


def extract_annotated_errors(content):
    """Extract text references and explanations from annotated error content.

    Args:
        content (str): Content containing <text> annotations

    Returns:
        list: List of tuples (error_text, explanation)
    """
    if not content or content.lower() == "none.":
        return []

    annotations = []
    # Find all <text>...</text> patterns and the explanation after them
    pattern = r"<text>(.*?)</text>\s*(.*?)(?=$|\n\s*-\s*<text>|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    for error_text, explanation in matches:
        # Clean up and add to annotations list
        error_text = error_text.strip()
        explanation = explanation.strip()
        if explanation.startswith("-"):
            explanation = explanation[1:].strip()
        annotations.append((error_text, explanation))

    return annotations


async def check_writing(
    language, level, exercise_text, writing_input, exercise_type, definitions, llm_provider: LLMProvider | None = None
):
    """Check the user's writing using the specified LLM provider.

    Args:
        language (str): The language code (e.g., "pl" for Polish)
        level (str): The proficiency level (e.g., "A1")
        exercise_text (str): The generated exercise text
        writing_input (str): The user's written response
        exercise_type (str): The type of exercise
        definitions (dict): Dictionary containing exercise definitions
        llm_provider (LLMProvider, optional): LLM provider to use. Uses default if None.

    Returns:
        tuple: (mistakes_list, style_errors_list, recommendations, cost)
                where mistakes_list and style_errors_list are lists of (text, explanation) tuples
    """
    from language_tutor.config import OR_MODEL_NAME_CHECK

    # Construct prompt for checking, asking for XML format with annotated text references
    prompt = f"""A student learning {language} was given the exercise for a {level} level '{exercise_type}' writing exercise:
'{exercise_text}'.

Their response was:
'{writing_input}'

Please check their writing. Provide feedback listing:
1. Grammatical mistakes.
2. Stylistic errors.
3. Recommendations for improvement.
4. Following the requirements of the exercise.

For mistakes and stylistic errors, 
wrap the specific problematic text in <text></text> tags, followed by your explanation. 
The text should be as specific as possible, and the explanation should be clear and educational.
Only strict grammatical mistakes should be included in the <mistakes> section. 
No recommendations or stylistic errors should be included in the <mistakes> section.
Format the output EXACTLY like this, using these specific XML tags:

<mistakes>
- <text>problematic text from the writing</text> explanation of the grammatical error. 
- <text>another error</text> explanation
(Or "None." if no strictly grammatical mistakes found. )
</mistakes>

<stylistic_errors>
- <text>stylistic issue</text> explanation of the stylistic issue
- <text>another issue</text> explanation
- <text></text> explanation if the recommendation is applicable to the whole text
( Or "None." if no stylistic errors found)
</stylistic_errors>

<recommendations>
List of recommendations for improvement
(Or "None." if no recommendations)
</recommendations>
"""
    messages = [{"role": "user", "content": prompt}]
    model_name = OR_MODEL_NAME_CHECK

    # Get LLM instance
    llm = llm_provider.get_llm() if llm_provider else get_llm()

    # Make the async API call
    response, cost = await llm.completion(model=model_name, messages=messages)
    feedback_content = response.choices[0].message.content

    # Log the response for debugging
    logger.info(f"Feedback response: {feedback_content}")

    # Parse XML tags
    mistakes_content = extract_content_from_xml(feedback_content, "mistakes", "")
    style_errors_content = extract_content_from_xml(
        feedback_content, "stylistic_errors", ""
    )
    recommendations = extract_content_from_xml(feedback_content, "recommendations", "")

    # Parse the annotations to get structured error data
    mistakes_list = extract_annotated_errors(mistakes_content)
    style_errors_list = extract_annotated_errors(style_errors_content)

    # Log the parsed results
    logger.info(f"Mistakes list: {mistakes_list}")
    logger.info(f"Style errors list: {style_errors_list}")
    logger.info(f"Recommendations: {recommendations}")

    return mistakes_list, style_errors_list, recommendations, cost


def format_mistakes_list(mistakes_list):
    """Format the mistakes list for display.

    Args:
        mistakes_list (list): List of tuples (error_text, explanation)

    Returns:
        str: Formatted string of mistakes
    """
    if not mistakes_list:
        return "No grammatical mistakes found."

    formatted_mistakes = []
    for error_text, explanation in mistakes_list:
        if error_text:
            formatted_mistakes.append(f"- {error_text}: {explanation}")
        else:
            formatted_mistakes.append(f"- {explanation}")

    return "\n".join(formatted_mistakes)
