##llm.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables at the very beginning
load_dotenv()

from backend.decision_lens import VENDOR_SELECTION_LENS  

def _check_openai_key():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found in environment. Please check your .env file.")

_check_openai_key()

client = OpenAI()

SYSTEM_PROMPT = """
You are a decision intelligence assistant.

You help users think clearly about trade-offs, risks, and assumptions.
You NEVER recommend actions or make decisions.
"""

async def call_llm(summaries, facts):
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

Return VALID JSON exactly in this format:

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content.strip()

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()