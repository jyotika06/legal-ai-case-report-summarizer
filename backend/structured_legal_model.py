import json
import re
from model_client import call_model
from text_chunker import chunk_text


# ----------------------------------------
# Clean model output
# ----------------------------------------
def clean_json_output(text):
    if not text:
        return ""

    text = text.replace("```json", "").replace("```", "")
    text = text.replace("`", "").replace("*", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ----------------------------------------
# Extract structured info from single chunk
# ----------------------------------------
def extract_chunk(chunk):

    prompt = f"""
You are a Structured Legal Information Model.

Extract legal information STRICTLY in this JSON format:

{{
    "metadata": {{
        "court": "",
        "case_title": "",
        "case_number": "",
        "judgment_date": "",
        "bench": []
    }},
    "parties": {{
        "appellant": "",
        "respondent": ""
    }},
    "acts": [],
    "sections": [],
    "citations": [],
    "facts": "",
    "issues": "",
    "arguments": {{
        "appellant": "",
        "respondent": ""
    }},
    "reasoning": "",
    "final_order": ""
}}

RULES:
- Return ONLY valid JSON.
- No explanations.
- Leave missing fields empty.
- Keep summaries concise.

TEXT:
{chunk}
"""

    raw_text = call_model(prompt)
    cleaned = clean_json_output(raw_text)

    try:
        return json.loads(cleaned)
    except Exception:
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            return json.loads(cleaned[start:end])
        except Exception:
            return {}


# ----------------------------------------
# Main function: Chunk + Merge
# ----------------------------------------
def extract_structured_legal_info(text):

    # Reduced chunk size for stability
    chunks = chunk_text(text, max_chars=12000)

    merged = {
        "metadata": {},
        "parties": {},
        "acts": [],
        "sections": [],
        "citations": [],
        "facts": "",
        "issues": "",
        "arguments": {},
        "reasoning": "",
        "final_order": ""
    }

    for chunk in chunks:
        part = extract_chunk(chunk)
        if not isinstance(part, dict):
            continue

        # Merge list fields safely
        for field in ["acts", "sections", "citations"]:
            value = part.get(field, [])
            if isinstance(value, list):
                merged[field] = list(set(merged[field] + value))

        # Merge dictionary fields safely
        for field in ["metadata", "parties", "arguments"]:
            value = part.get(field, {})
            if isinstance(value, dict):
                merged[field].update(value)

        # Merge text fields safely
        for field in ["facts", "issues", "reasoning", "final_order"]:
            value = part.get(field, "")
            if isinstance(value, str) and value.strip():
                cleaned_text = value.strip()
                if merged[field]:
                    if cleaned_text not in merged[field]:
                        merged[field] += "\n" + cleaned_text
                else:
                    merged[field] = cleaned_text

    return merged