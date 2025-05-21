"""Utility functions for the Language Tutor app."""

import re
import random
import asyncio
import nest_asyncio
from language_tutor.llm import llm
from PyQt5.QtWidgets import QApplication

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
    from language_tutor.config import OR_MODEL_NAME
    
    # Construct prompt asking for specific formatting
    prompt = f"""Create a short '{exercise_type}' writing exercise for a learner of {language} for a proficiency level {level}.
    The expected length of the writing should be between {definitions[exercise_type]['expected_length'][0]} and {definitions[exercise_type]['expected_length'][1]} words.
    Random number is {random.randint(1, 10000)} (don't use it, it is just to make the prompt different). 
Provide the exercise text and optionally some hints. The requirements for the exercise are:
'{definitions[exercise_type]['requirements']}'
You should generate exactly one exercise. It should be a task, not the text of the exercise itself.

Format the output EXACTLY like this, using these specific headings:

**Exercise:**
[The exercise text goes here]

**Hints:**
[Optional hints go here. You can add useful phrases in addition to the hints. If no hints, write "None."]
"""
    messages = [{"role": "user", "content": prompt}]

    # Make the async API call
    response, cost = await llm.completion(model=OR_MODEL_NAME, messages=messages)

    full_response_content = response.choices[0].message.content

    # --- Basic Parsing ---
    exercise_match = re.search(r"\*\*Exercise:\*\*\n(.*?)\n\*\*Hints:\*\*", full_response_content, re.DOTALL | re.IGNORECASE)
    hints_match = re.search(r"\*\*Hints:\*\*\n(.*)", full_response_content, re.DOTALL | re.IGNORECASE)

    if exercise_match:
        exercise_text = exercise_match.group(1).strip()
    else:
        # Fallback if parsing fails
        exercise_text = full_response_content.split("**Hints:**")[0].replace("**Exercise:**", "").strip()

    if hints_match:
        hints = hints_match.group(1).strip()
        if hints.lower() == "none.":
            hints = ""  # Clear if hints are explicitly none
    else:
        # Fallback if parsing fails
        hints = ""  # Assume no hints if parsing fails

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
    
    # Construct prompt for checking, asking for specific format
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
Format the output EXACTLY like this, using these specific headings:

**Mistakes:**
[List of grammatical mistakes, or "None." if none found]

**Stylistic Errors:**
[List of stylistic errors, or "None." if none found]

**Recommendations:**
[List of recommendations, or "None." if none found]
"""
    messages = [{"role": "user", "content": prompt}]
    model_name = OR_MODEL_NAME_CHECK

    # Make the async API call
    response, cost = await llm.completion(model=model_name, messages=messages)
    feedback_content = response.choices[0].message.content

    # --- Basic Parsing ---
    mistakes_match = re.search(r"\*\*Mistakes:\*\*\n(.*?)\n\*\*Stylistic Errors:\*\*", feedback_content, re.DOTALL | re.IGNORECASE)
    style_match = re.search(r"\*\*Stylistic Errors:\*\*\n(.*?)\n\*\*Recommendations:\*\*", feedback_content, re.DOTALL | re.IGNORECASE)
    recs_match = re.search(r"\*\*Recommendations:\*\*\n(.*)", feedback_content, re.DOTALL | re.IGNORECASE)

    mistakes = mistakes_match.group(1).strip() if mistakes_match else "Could not parse."
    style_errors = style_match.group(1).strip() if style_match else "Could not parse."
    recommendations = recs_match.group(1).strip() if recs_match else "Could not parse."
    
    # Return empty strings instead of "None." to avoid displaying it
    mistakes = "" if mistakes.lower() == "none." else mistakes
    style_errors = "" if style_errors.lower() == "none." else style_errors
    recommendations = "" if recommendations.lower() == "none." else recommendations

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
    response, cost = await llm.completion(model=model, messages=messages)
    
    # Get the response
    answer = response.choices[0].message.content
    return answer, cost

def run_async(coro, in_q_application=True):
    """Run an async coroutine from a synchronous method without blocking UI.
    
    Args:
        coro: The coroutine to run
        in_q_application: Whether running in Qt application
    """
    
    # Apply nest_asyncio to allow nested event loops
    try:
        nest_asyncio.apply()
    except RuntimeError:
        # If already applied or not needed, continue
        pass
    
    # Get or create an event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Create a future for the coroutine
    future = asyncio.ensure_future(coro)
    
    # Process Qt events while waiting for the coroutine to complete
    if in_q_application:
        while not future.done():
            QApplication.processEvents()
            loop.run_until_complete(asyncio.sleep(0.01))  # Short sleep to avoid CPU hogging
    else:
        # If not in Qt application, just run the event loop until the coroutine is done
        loop.run_until_complete(future)    
    # Return the result
    return future.result()