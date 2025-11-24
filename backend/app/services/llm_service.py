import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import google.generativeai as genai
import json

# ✅ LOCAL KEY — do NOT commit to GitHub
GENAI_API_KEY = "AIzaSyBQyqfzfAV51FGBIQNc4nsOybjQ2jRsG-c"

genai.configure(api_key=GENAI_API_KEY)

# ✅ Recommended model
model = genai.GenerativeModel("gemini-2.5-flash")


# ✅ Generate section content using title + doc type
def llm_generate_section(section_title: str, doc_type: str, context_summary: str):
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
    - Do NOT include the section title in the output
    - Match the expected style for {doc_type.upper()}
    """

    response = model.generate_content(prompt)
    return response.text.strip()


# ✅ Evaluate quality and provide improvement direction
def llm_evaluate(content: str):
    prompt = f"""
    Evaluate the following document section and respond ONLY in JSON.

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
    text = response.text.strip().replace("```json", "").replace("```", "")

    try:
        return json.loads(text)
    except:
        return {"score": 7.5, "improvement_focus": "Improve clarity and flow"}


# ✅ Refinement based on focus or user dislike
def llm_refine(content: str, improvement_focus: str, user_prompt=None):
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
    - Return ONLY the improved text
    """

    response = model.generate_content(prompt)
    return response.text.strip()
def llm_refine_outline(raw_outline: list, doc_type: str):
    prompt = f"""
    You are refining a user-provided {doc_type.upper()} document outline.

    ORIGINAL OUTLINE:
    {raw_outline}

    Requirements:
    - Keep the user's ORIGINAL ideas and intent
    - Do NOT add new topics not present in the outline
    - You MAY rename sections for clarity
    - You MAY reorder only if it improves logical flow
    - You MUST preserve meaning
    - Return ONLY a clean JSON list of section titles

    Example output:
    ["Introduction", "Problem Statement", "Methodology", "Conclusion"]
    """

    response = model.generate_content(prompt)

    import json
    text = response.text.strip().replace("```json", "").replace("```", "")

    try:
        return json.loads(text)
    except:
        # fallback — return original
        return raw_outline

