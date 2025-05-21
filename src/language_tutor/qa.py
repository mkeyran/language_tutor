"""Question answering utilities for Language Tutor."""

from language_tutor.llm import llm


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
