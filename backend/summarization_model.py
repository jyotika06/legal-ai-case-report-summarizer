import json
from model_client import call_model


def summarize_text(text):

    prompt = f"""
You are a Legal Document Summarization Model.

Return STRICT JSON in this format:

{{
    "bullet_summary": ["point 1", "point 2"],
    "paragraph_summary": "5-7 line readable summary.",
    "issues_summary": ["issue 1", "issue 2"]
}}

RULES:
- Return ONLY valid JSON.
- No markdown.
- No explanations.
- Keep summaries concise.

TEXT:
{text}
"""

    raw_text = call_model(prompt)

    if not raw_text:
        return _fallback_response("Empty model response")

    cleaned = (
        raw_text.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        parsed = json.loads(cleaned)
        return _validate_summary_structure(parsed)

    except Exception:
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            parsed = json.loads(cleaned[start:end])
            return _validate_summary_structure(parsed)
        except Exception:
            return _fallback_response(cleaned)


# ----------------------------------------
# Validate JSON structure
# ----------------------------------------
def _validate_summary_structure(data):

    if not isinstance(data, dict):
        return _fallback_response("Invalid JSON structure")

    return {
        "bullet_summary": data.get("bullet_summary", []),
        "paragraph_summary": data.get("paragraph_summary", ""),
        "issues_summary": data.get("issues_summary", [])
    }


# ----------------------------------------
# Fallback response
# ----------------------------------------
def _fallback_response(raw_text):

    return {
        "bullet_summary": ["Failed to parse structured summary"],
        "paragraph_summary": raw_text if isinstance(raw_text, str) else "",
        "issues_summary": []
    }