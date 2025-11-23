import os
import google.generativeai as genai

# Load Gemini API key from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")


# 1️⃣ Generate initial or retry content
def llm_generate(section_id: int, content=None):
    prompt = f"""
    You are generating content for a document section.

    Section ID: {section_id}

    Provide a clear, well-written paragraph of 150-200 words.
    Do NOT mention the section ID.
    """

    response = model.generate_content(prompt)
    return response.text.strip()


# 2️⃣ Evaluate content and return score
def llm_evaluate(content: str):
    prompt = f"""
    You are evaluating the following text for quality.

    Text:
    \"\"\"{content}\"\"\"

    Score it from 1 to 10 based on:
    - clarity
    - relevance
    - coherence
    - structure

    Respond ONLY in JSON:
    {{
        "score": <number>,
        "feedback": "<short explanation>"
    }}
    """

    response = model.generate_content(prompt)
    import json
    return json.loads(response.text.strip())


# 3️⃣ Refine based on feedback or user instruction
def llm_refine(content: str, feedback=None, user_prompt=None):
    prompt = f"""
    Improve the following text.

    ORIGINAL:
    \"\"\"{content}\"\"\"

    FEEDBACK TO FIX:
    {feedback or "Improve clarity and flow."}

    USER REFINEMENT REQUEST:
    {user_prompt or "None"}

    Rules:
    - Keep the meaning the same
    - Do NOT shorten too much
    - Return only the improved text
    """

    response = model.generate_content(prompt)
    return response.text.strip()
