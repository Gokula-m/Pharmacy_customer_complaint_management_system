"""
Thin wrapper around the Groq API.

Get a free API key at https://console.groq.com -> API Keys -> Create API Key,
then put it in backend/.env as GROQ_API_KEY=gsk_...

Models used (see https://console.groq.com/docs/models):
  - gemma2-9b-it            : fast, cheap -> extraction, completeness checking
  - llama-3.3-70b-versatile : stronger reasoning -> QMS severity/risk reasoning, summary
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load backend/.env explicitly by path, so this works no matter which
# directory uvicorn/python is launched from.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FAST_MODEL = "openai/gpt-oss-20b"
REASONING_MODEL = "openai/gpt-oss-120b"


def call_llm(system_prompt: str, user_prompt: str, model: str = FAST_MODEL,
             json_mode: bool = False, temperature: float = 0.2) -> str:
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = _client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return response.choices[0].message.content.strip()


def call_llm_json(system_prompt: str, user_prompt: str, model: str = FAST_MODEL) -> dict:
    """Call the LLM and parse a JSON object from the response, tolerating stray markdown fences."""
    raw = call_llm(system_prompt, user_prompt, model=model, json_mode=True)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to locate the outermost { ... }
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start:end + 1])
        raise
