"""Claude API wrapper with system prompts and graceful fallbacks for MedBridge AI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename: str) -> dict[str, Any]:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def _clean(val: str | None) -> str:
    val = (val or "").strip()
    return val if val and val != "your-api-key-here" else ""


def _openrouter_key() -> str:
    return _clean(os.getenv("OPENROUTER_API_KEY"))


def _anthropic_key() -> str:
    return _clean(os.getenv("ANTHROPIC_API_KEY"))


def _openrouter_model() -> str:
    return _clean(os.getenv("OPENROUTER_MODEL")) or "anthropic/claude-sonnet-4.5"


def has_api_key() -> bool:
    return bool(_openrouter_key() or _anthropic_key())


def _get_openrouter_client():
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "The `openai` package is not installed. Run `pip install openai`."
        ) from exc
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=_openrouter_key())


def _get_anthropic_client():
    try:
        from anthropic import Anthropic  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "The `anthropic` package is not installed. Run `pip install anthropic`."
        ) from exc
    return Anthropic(api_key=_anthropic_key())


def build_navigator_system_prompt() -> str:
    programs = _load_json("programs.json")
    programs_text = json.dumps(programs, indent=2)
    return f"""You are MedBridge AI, a healthcare navigation assistant for underserved communities. Your job is to help patients find healthcare programs, clinics, and financial assistance they qualify for based on their specific situation.

You have access to the following local healthcare programs database for the Brazos Valley, Texas area:

{programs_text}

When the user describes their situation, you should:
1. Identify their key needs (insurance status, income level, health conditions, location)
2. Match them to 2-5 relevant programs from the database
3. Explain WHY each program is a good match for their specific situation
4. Provide clear next steps for each program (who to call, what to bring, how to apply)
5. Use simple, plain language at a 6th-grade reading level
6. If you detect emergency symptoms (chest pain, difficulty breathing, severe bleeding), immediately advise calling 911 and provide the nearest ER location (St. Joseph Health Bryan — 2801 Franciscan Dr, Bryan TX).

Always be warm, empathetic, and actionable. Don't just list programs — explain why they matter for THIS person's situation.

Format your response with clear sections for each recommended program using markdown headers (###) and bullet points. End with a short, encouraging "next step" call to action.

At the very end of your response, on its own line, emit a machine-readable list of matched program IDs in this exact format (no other text after it):
MATCHED_IDS: id1, id2, id3
"""


def build_screen_check_system_prompt() -> str:
    guidelines = _load_json("uspstf_guidelines.json")
    return f"""You are MedBridge AI's Preventive Screening Advisor. You use USPSTF guidelines to build a personalized preventive screening plan.

USPSTF reference data:
{json.dumps(guidelines, indent=2)}

Given a patient's profile (age, sex, smoking status, family history, existing conditions), respond with ONLY valid JSON (no markdown fences) using this schema:
{{
  "screenings": [{{
    "name": "",
    "status": "OVERDUE|UPCOMING|ON_TRACK|NOT_APPLICABLE",
    "due_date_relative": "e.g. 'Now', 'Within 6 months', 'In 2 years'",
    "why_it_matters": "Plain-language reason tailored to this patient",
    "where_to_go": "Suggested Brazos Valley provider (e.g., Brazos Valley Community Health Center, St. Joseph Health Bryan, Baylor Scott & White College Station)"
  }}],
  "top_priority": "Which 1-2 screenings should this person do first, and why",
  "lifestyle_notes": "Short, encouraging lifestyle recommendations based on profile"
}}
"""


def build_recovery_coach_system_prompt() -> str:
    return """You are MedBridge AI's Recovery Coach. You turn hospital discharge instructions into a clear day-by-day recovery plan a patient can actually follow.

Given discharge instructions, respond with ONLY valid JSON (no markdown fences) using this schema:
{
  "condition": "Short label of the condition the patient is recovering from",
  "overview": "2-3 sentence plain-language summary of what to expect",
  "phases": [
    {
      "label": "Day 1-3: Rest phase",
      "days": "1-3",
      "medications": [{"name": "", "dose": "", "schedule": ""}],
      "activity": "",
      "diet": "",
      "red_flags": ["Symptom 1", "Symptom 2"]
    }
  ],
  "follow_up": "When and with whom the patient should follow up",
  "emergency_symptoms": ["Symptoms that mean call 911 immediately"]
}
Include at least 3 phases covering the full recovery window.
"""


def build_formfill_system_prompt() -> str:
    return """You are MedBridge AI's Insurance FormFill assistant. Given plain-English answers about a household, you recommend which public or subsidized insurance programs they likely qualify for (Medicaid, CHIP, ACA Marketplace with subsidies, Medicare) and generate a pre-filled application summary.

Respond with ONLY valid JSON (no markdown fences) using this schema:
{
  "eligibility": [
    {"program": "", "likely_qualifies": true, "reason": "", "how_to_apply": ""}
  ],
  "next_steps": ["Step 1", "Step 2"],
  "application_summary": "A pre-filled, printable application summary the user can download as PDF. Use short labeled lines (Name:, State:, Household size:, Annual income:, Current insurance:, Special circumstances:, Likely programs:) suitable for fpdf2 rendering."
}
"""


def _call_openrouter(system_prompt: str, history: list[dict], max_tokens: int) -> str:
    client = _get_openrouter_client()
    messages = [{"role": "system", "content": system_prompt}, *history]
    response = client.chat.completions.create(
        model=_openrouter_model(),
        max_tokens=max_tokens,
        messages=messages,
        extra_headers={
            "HTTP-Referer": "https://medbridge-ai.local",
            "X-Title": "MedBridge AI",
        },
    )
    return response.choices[0].message.content or ""


def _call_anthropic(system_prompt: str, history: list[dict], max_tokens: int) -> str:
    client = _get_anthropic_client()
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=history,
    )
    return response.content[0].text


def _dispatch(system_prompt: str, history: list[dict], max_tokens: int) -> str:
    if not has_api_key():
        raise RuntimeError("No API key configured — use Demo Mode or add a key to .env.")
    try:
        if _openrouter_key():
            return _call_openrouter(system_prompt, history, max_tokens)
        return _call_anthropic(system_prompt, history, max_tokens)
    except Exception as exc:
        raise RuntimeError(f"AI request failed: {exc}") from exc


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
    """Single-turn call. Returns the model's text response."""
    return _dispatch(system_prompt, [{"role": "user", "content": user_message}], max_tokens)


def call_claude_chat(system_prompt: str, history: list[dict], max_tokens: int = 2000) -> str:
    """Multi-turn chat. History is a list of {'role': 'user'|'assistant', 'content': str}."""
    return _dispatch(system_prompt, history, max_tokens)


def extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from a model response, tolerant of markdown fences or prose wrappers."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
    return json.loads(text[start : end + 1])


def load_programs() -> list[dict]:
    return _load_json("programs.json")["programs"]


def load_uspstf_guidelines() -> list[dict]:
    return _load_json("uspstf_guidelines.json")["guidelines"]
