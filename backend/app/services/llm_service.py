import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv  # if you're already using this elsewhere, it's fine

# Load the local .env if it lives alongside the app package, then fall back to defaults
package_dir = Path(__file__).resolve().parent.parent
load_dotenv(package_dir / ".env")
load_dotenv()

# ✅ Read key from environment instead of hard-coding
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not GENAI_API_KEY:
    # Fail loudly so you know it's misconfigured rather than silently calling with None
    raise RuntimeError("GENAI_API_KEY is not set. Please add it to your .env file.")

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
    focus = (user_prompt or improvement_focus or "").strip() or "Improve clarity, structure, and conciseness."

    prompt = f"""
You are revising a document section. Your job is to MODIFY the text so that it clearly responds to the REVISION REQUEST.

REVISION REQUEST:
\"\"\"{focus}\"\"\"

CURRENT TEXT:
\"\"\"{content}\"\"\"

Rewrite the CURRENT TEXT according to the request above.

Very important requirements:
- You MUST change the wording in a meaningful way; do NOT return the original text unchanged.
- Keep the same core meaning and key facts.
- Improve clarity, structure, and flow **specifically** in line with the revision request.
- Keep roughly the same length (+/- 15%).
- Avoid repeating entire sentences verbatim unless they are technical terms or names.
- The changes should be clearly noticeable to a human reader.
- Return ONLY the revised text, with no explanations, no bullet points, no markdown.
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