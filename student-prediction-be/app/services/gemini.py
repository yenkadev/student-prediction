import json
import logging
import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent.parent.parent / ".env")
_MODEL = "gemini-3.1-flash-lite"
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client

async def extract_fields(turns: list[dict], required_fields: list[str]) -> dict:
    """
    Given conversation turns, ask Gemini to extract all available field values.
    Returns a dict of {field_name: value_or_None}.
    """
    conversation_text = "\n".join(
        f"{t['role'].upper()}: {t['content']}" for t in turns
    )

    prompt = f"""You are extracting student academic data from a conversation.

Required fields: {required_fields}

Conversation:
{conversation_text}

Extract all field values mentioned in the conversation. Return ONLY valid JSON with this structure:
{{"field_name": value_or_null}}

For numeric fields (GPA, Attendance_Rate, Stress_Index, Study_Hours_per_Day, Assignment_Delay_Days, Travel_Time_Minutes, Age, Family_Income, Semester_GPA, CGPA): return numbers.
For categorical fields (Gender, Internet_Access, Part_Time_Job, Scholarship, Semester, Department, Parental_Education): return strings exactly as mentioned.
If a field is not mentioned, return null for it.
Return ONLY the JSON object, no markdown, no explanation."""

    response = await _get_client().aio.models.generate_content(model=_MODEL, contents=prompt)
    if not response.text:
        raise ValueError("Gemini returned an empty response")
    text = response.text.strip()
    # Strip markdown code fences if present (handle ```json, ```JSON, etc.)
    if text.startswith("```"):
        # Drop first line (fence + optional lang tag), strip any trailing backticks
        text = "\n".join(text.split("\n")[1:]).rstrip("`").strip()
    try:
        extracted = json.loads(text.strip())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse Gemini response as JSON")
    result = {field: extracted.get(field) for field in required_fields}
    present = {k: v for k, v in result.items() if v is not None}
    missing = [k for k, v in result.items() if v is None]
    present_lines = "\n".join(f"  {k}: {v}" for k, v in present.items())
    logger.debug("🟨 [GEMINI:EXTRACT] %d/%d fields:\n%s", len(present), len(required_fields), present_lines)
    if missing:
        logger.debug("🟥 [GEMINI:MISSING]\n  %s", "\n  ".join(missing))
    return result


async def generate_followup_question(turns: list[dict], missing_fields: list[str]) -> str:
    """
    Ask Gemini to generate a natural follow-up question asking for the missing fields.
    """
    prompt = f"""You are a friendly academic advisor chatbot collecting student information to assess dropout risk.

The conversation so far:
{chr(10).join(f"{t['role'].upper()}: {t['content']}" for t in turns)}

Still missing information: {missing_fields}

Generate a single, natural, conversational question asking for the missing information.
Be concise. Ask for all missing fields in one question if possible.
Return ONLY the question text, no extra explanation."""

    response = await _get_client().aio.models.generate_content(model=_MODEL, contents=prompt)
    if not response.text:
        raise ValueError("Gemini returned an empty response")
    return response.text.strip()
