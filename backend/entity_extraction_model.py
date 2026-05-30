import json
from model_client import call_model


def extract_entities(text):

    prompt = f"""
You are a Legal Metadata Extraction Model.

Extract structured legal metadata ONLY in the JSON structure below.

IMPORTANT:
- Keep summaries SHORT and concise.
- Return ONLY valid JSON.
- If data missing → leave empty.

{{
    "metadata": {{
        "court": "",
        "case_title": "",
        "case_number": "",
        "judgment_date": "",
        "bench": [],
        "parties": {{
            "appellant": "",
            "respondent": ""
        }}
    }},
    "sections": [],
    "acts": [],
    "citations": [],
    "facts": "",
    "issues": "",
    "arguments": {{
        "appellant": "",
        "respondent": ""
    }},
    "reasoning": "",
    "final_order": "",
    "compensation": {{
        "amounts": [],
        "highest_amount": ""
    }}
}}

TEXT:
{text}
"""

    raw_text = call_model(prompt)

    cleaned = (
        raw_text.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(cleaned)
    except Exception:
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            return json.loads(cleaned[start:end])
        except Exception:
            return {"error": "Failed to parse JSON", "raw_output": cleaned}