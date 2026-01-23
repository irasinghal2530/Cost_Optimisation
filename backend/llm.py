##llm.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables at the very beginning
load_dotenv()

from backend.decision_lens import VENDOR_SELECTION_LENS  

def _check_gemini_key():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY not found in environment. Please check your .env file.")

_check_gemini_key()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are a decision intelligence assistant.
You help users think clearly about trade-offs, risks, and assumptions.
You NEVER recommend actions or make decisions.
"""

async def call_llm(summaries, facts):
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        system_instruction=SYSTEM_PROMPT
    )
    
    prompt = f"""
You are analyzing vendor and procurement information.

DECISION LENS (how this company evaluates vendors):
{VENDOR_SELECTION_LENS}

IMPORTANT:
- VERIFIED FACTS are programmatically extracted and should be trusted
- DOCUMENT CONTEXT provides background and nuance only
- If facts and documents conflict, prefer FACTS

YOUR TASK:
- Use the decision lens to interpret the facts
- Use bullet points (2–3 lines per point)
- Surface implicit assumptions
- Highlight missing or weak information
- Explain risks and trade-offs
- Do NOT recommend vendors
- Do NOT rank vendors
- Do NOT suggest negotiation tactics

Return ONLY VALID JSON exactly in this format:

{{
  "insights": [],
  "assumptions": [],
  "missing_information": [],
  "risks": [],
  "tradeoffs": []
}}

VERIFIED FACTS:
{json.dumps(facts, indent=2)}

DOCUMENT CONTEXT:
{json.dumps(summaries, indent=2)}
"""

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    raw = response.text.strip()

    try:
        return json.loads(raw)
    except Exception:
        print("⚠️ RAW LLM OUTPUT:\n", raw)
        return {
            "insights": ["Analysis formatting error"],
            "assumptions": ["LLM response could not be parsed cleanly"],
            "missing_information": [],
            "risks": ["Analysis incomplete due to formatting issue"],
            "tradeoffs": []
        }

async def chat_reply(question, context):
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        system_instruction=SYSTEM_PROMPT
    )
    
    prompt = f"""
Context (do not repeat verbatim):
{json.dumps(context, indent=2)}

User question:
"{question}"

RULES:
- Respond in plain English paragraphs
- Respond in a few lines in bullet points
- Ask thoughtful questions when helpful
- Explain trade-offs, risks, and assumptions
- DO NOT use JSON
- DO NOT recommend actions
- DO NOT choose vendors
"""

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.4
        )
    )

    return response.text.strip()