import json

import google.generativeai as genai

# ✅ LOCAL KEY — do NOT commit to GitHub
GENAI_API_KEY = "AIzaSyAx_wBwzSF33EQkYCz4KI_gc6Q2kDCLAIM"

genai.configure(api_key=GENAI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def llm_generate_section(section_title: str, doc_type: str, context_summary: str) -> str:
    """
    Generate a professional document section based on a title, document type,
    and contextual summary.

    Parameters:
        section_title (str): Title of the section to be generated.
        doc_type (str): Type of document (e.g., report, proposal).
        context_summary (str): Short contextual summary guiding the output.

    Returns:
        str: Generated section text.
    """
    prompt = f"""
    Generate detailed content for a {doc_type.upper()} document section titled:

    "{section_title}"

    Context:
    \"\"\"{context_summary}\"\"\"

    Requirements:
    - 180–220 words
    - Professional and coherent tone
    - Single flowing paragraph
    - No repetition
    - Do not include the section title in the output
    - Match the expected style for {doc_type.upper()}
    """

    response = model.generate_content(prompt)
    return response.text.strip()


def llm_evaluate(content: str) -> dict:
    """
    Evaluate the quality of a generated section and return a structured score
    and improvement recommendation.

    Parameters:
        content (str): The text to evaluate.

    Returns:
        dict: {
            "score": float,
            "improvement_focus": str
        }
    """
    prompt = f"""
    Evaluate the following document section and respond only in JSON.

    Text:
    \"\"\"{content}\"\"\"

    Score 1–10 based on:
    - clarity
    - relevance
    - structure
    - depth

    JSON response format:
    {{
      "score": <number>,
      "improvement_focus": "<one short sentence>"
    }}
    """

    response = model.generate_content(prompt)
    cleaned = response.text.strip().replace("```json", "").replace("```", "")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "score": 7.5,
            "improvement_focus": "Improve clarity and flow"
        }


def llm_refine(content: str, improvement_focus: str, user_prompt: str = None) -> str:
    """
    Refine existing content based on either an automated improvement focus
    or a specific user instruction.

    Parameters:
        content (str): Existing text to refine.
        improvement_focus (str): Model-determined improvement direction.
        user_prompt (str, optional): Explicit user request overriding the focus.

    Returns:
        str: Refined text.
    """
    prompt = f"""
    Improve the following section.

    USER REQUEST:
    "{user_prompt or improvement_focus}"

    CURRENT TEXT:
    \"\"\"{content}\"\"\"

    Rules:
    - Preserve meaning
    - Improve clarity and structure
    - Maintain similar length
    - Return only the improved text
    """

    response = model.generate_content(prompt)
    return response.text.strip()


def llm_refine_outline(raw_outline: list, doc_type: str) -> list:
    """
    Refine a user-provided document outline while preserving its meaning and scope.

    Parameters:
        raw_outline (list): List of user-provided section titles.
        doc_type (str): Type of document.

    Returns:
        list: Cleaned and logically ordered outline.
    """
    prompt = f"""
    You are refining a user-provided {doc_type.upper()} document outline.

    ORIGINAL OUTLINE:
    {raw_outline}

    Requirements:
    - Keep the user's original ideas and intent
    - Do not add new topics
    - Renaming sections for clarity is allowed
    - Reordering is allowed only if it improves flow
    - Preserve meaning
    - Return only a clean JSON list of section titles

    Example output:
    ["Introduction", "Problem Statement", "Methodology", "Conclusion"]
    """

    response = model.generate_content(prompt)
    cleaned = response.text.strip().replace("```json", "").replace("```", "")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return raw_outline
