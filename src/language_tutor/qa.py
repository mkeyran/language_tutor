"""Question answering utilities for Language Tutor."""

from language_tutor.llm import get_llm, LLMProvider


async def answer_question(model, question, context, llm_provider: LLMProvider | None = None):
    """Answer a question using the specified AI model and LLM provider.

    Args:
        model (str): The AI model identifier
        question (str): The user's question
        context (dict): Dictionary containing context information
        llm_provider (LLMProvider, optional): LLM provider to use. Uses default if None.

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

    # Get LLM instance
    llm = llm_provider.get_llm() if llm_provider else get_llm()
    
    # Make the API call
    messages = [{"role": "user", "content": prompt}]
    response, cost = await llm.completion(model=model, messages=messages)

    # Get the response
    answer = response.choices[0].message.content
    return answer, cost
