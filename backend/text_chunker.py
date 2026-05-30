import re

def chunk_text(text, max_chars=12000):
    """
    Splits long legal text into safe model-sized chunks.
    Avoids breaking sentences abruptly.
    """

    if not text:
        return []

    text = re.sub(r"\s+", " ", text).strip()

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_chars, text_length)

        if end < text_length:
            # Try to break at sentence boundary
            sentence_break = max(
                text.rfind(". ", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end)
            )
            if sentence_break != -1:
                end = sentence_break + 1

        chunks.append(text[start:end].strip())
        start = end

    return chunks