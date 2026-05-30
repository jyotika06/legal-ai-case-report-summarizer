import re
from model_client import call_model

# ----------------------------------------
# In-memory conversation history
# ----------------------------------------
CHAT_HISTORY = []  # resets when backend restarts


# ----------------------------------------
# Clean model output
# ----------------------------------------
def clean_ai_text(text):

    if not text:
        return ""

    # Remove markdown formatting
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)

    # Remove headings
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)

    # Normalize bullets
    text = re.sub(r"^- ", "• ", text, flags=re.MULTILINE)

    # Clean spacing
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


# ----------------------------------------
# Conversational Legal AI Engine
# ----------------------------------------
def ask_legal_ai(question, context_text):

    global CHAT_HISTORY

    if not question:
        return "Please enter a valid question."

    # Store user question
    CHAT_HISTORY.append({"role": "user", "text": question})

    judgment_loaded = bool(context_text.strip())

    # Build limited conversation memory
    conversation = ""
    for msg in CHAT_HISTORY[-8:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation += f"{role}: {msg['text']}\n"

    # Structured system instruction
    system_prompt = f"""
You are a Conversational Legal Intelligence Model.

Your objectives:
- Maintain natural dialogue.
- Understand follow-up questions.
- Maintain short-term conversational memory.
- Avoid repetitive generic responses.
- Never hallucinate case facts.

Rules:
1. If no judgment is uploaded:
   - Answer general legal questions.
   - If user indicates they will upload a file, respond politely and briefly.

2. If judgment is uploaded:
   - Use ONLY provided judgment context.
   - If answer not found, say:
     "This judgment does not mention that specifically, but here is the general legal understanding."

3. Keep responses concise and professional.
4. No markdown formatting.

Recent Conversation:
{conversation}

Uploaded Judgment Context:
{context_text}
"""

    full_prompt = f"{system_prompt}\nUser Question:\n{question}"

    try:
        raw_answer = call_model(full_prompt, temperature=0.3)

        final_answer = clean_ai_text(raw_answer)

        CHAT_HISTORY.append({"role": "assistant", "text": final_answer})

        return final_answer

    except Exception as e:
        print("Model API Error:", e)
        return "⚠ Unable to process your request at the moment."