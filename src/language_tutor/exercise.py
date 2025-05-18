"""Exercise-related utilities for Language Tutor."""

import re
import random
from language_tutor.llm import llm
from language_tutor.config import OR_MODEL_NAME

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

async def generate_exercise(language, level, exercise_type, definitions):
    """Generate a new language exercise using LiteLLM.

    Args:
        language (str): The language code (e.g., "pl" for Polish)
        level (str): The proficiency level (e.g., "A1")
        exercise_type (str): The type of exercise to generate
        definitions (dict): Dictionary containing exercise definitions

    Returns:
        tuple: (exercise_text, hints, cost)
    """
    # Construct prompt asking for specific formatting
    prompt = f"""Create a short '{exercise_type}' writing exercise for a learner of {language} for a proficiency level {level}.
    The expected length of the writing should be between {definitions[exercise_type]['expected_length'][0]} and {definitions[exercise_type]['expected_length'][1]} words.
    Random number is {random.randint(1, 10000)} (don't use it, it is just to make the prompt different).
Provide the exercise text and optionally some hints. The requirements for the exercise are:
'{definitions[exercise_type]['requirements']}'
You should generate exactly one exercise. It should be a task, not the text of the exercise itself.

Format the output EXACTLY like this, using these specific XML tags:

<exercise>
The exercise text goes here
</exercise>

<hints>
Optional hints go here. You can add useful phrases in addition to the hints. If no hints, write "None."
</hints>
"""
    messages = [{"role": "user", "content": prompt}]

    # Make the async API call
    response, cost = await llm.completion(model=OR_MODEL_NAME, messages=messages)

    full_response_content = response.choices[0].message.content

    # Parse XML output
    exercise_text = extract_content_from_xml(full_response_content, "exercise")
    hints = extract_content_from_xml(full_response_content, "hints", "")

    return exercise_text, hints, cost


async def check_writing(language, level, exercise_text, writing_input, exercise_type, definitions):
    """Check the user's writing using LiteLLM.

    Args:
        language (str): The language code (e.g., "pl" for Polish)
        level (str): The proficiency level (e.g., "A1")
        exercise_text (str): The generated exercise text
        writing_input (str): The user's written response
        exercise_type (str): The type of exercise
        definitions (dict): Dictionary containing exercise definitions

    Returns:
        tuple: (mistakes, style_errors, recommendations, cost)
    """
    from language_tutor.config import OR_MODEL_NAME_CHECK
    
    # Construct prompt for checking, asking for XML format
    prompt = f"""A student learning {language} was given the exercise:
'{exercise_text}' with the following requirements:
'{definitions[exercise_type]['requirements']}'

Their response was:
'{writing_input}'

Please check their writing. Provide feedback listing:
1. Grammatical mistakes.
2. Stylistic errors.
3. Recommendations for improvement.
4. Following the requirements of the exercise.
Format the output EXACTLY like this, using these specific XML tags:

<mistakes>
List of grammatical mistakes, or "None." if none found
</mistakes>

<stylistic_errors>
List of stylistic errors, or "None." if none found
</stylistic_errors>

<recommendations>
List of recommendations, or "None." if none found
</recommendations>
"""
    messages = [{"role": "user", "content": prompt}]
    model_name = OR_MODEL_NAME_CHECK

    # Make the async API call
    response, cost = await llm.completion(model=model_name, messages=messages)
    feedback_content = response.choices[0].message.content

    # Parse XML tags
    mistakes = extract_content_from_xml(feedback_content, "mistakes", "")
    style_errors = extract_content_from_xml(feedback_content, "stylistic_errors", "")
    recommendations = extract_content_from_xml(feedback_content, "recommendations", "")

    return mistakes, style_errors, recommendations, cost


async def answer_question(model, question, context):
    """Answer a question using the specified AI model.
    
    Args:
        model (str): The AI model identifier
        question (str): The user's question
        context (dict): Dictionary containing context information
        
    Returns:
        tuple: (answer_text, cost)
    """
    # Construct the prompt
    prompt = f"""You are a helpful language learning assistant. The user is learning {context['language']} 
at {context['level']} level. They are working on a {context['exercise_type']} exercise:

"{context['exercise']}"

The user's question is:
{question}

Please provide a helpful, educational response focused on language learning."""
    
    # Make the API call
    messages = [{"role": "user", "content": prompt}]
    response = await litellm.acompletion(
        model=model, 
        messages=messages, 
        api_base=litellm.base_url
    )
    
    # Try to calculate cost
    model_name = model.split("/")[-1].split(":")[0]
    if model_name in MODEL_PRICE_PER_TOKEN:
        cost = completion_cost(response, custom_cost_per_token=MODEL_PRICE_PER_TOKEN[model_name])
    else:
        cost = None
    
    # Get the response
    answer = response.choices[0].message.content
    return answer, cost