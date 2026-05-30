import re


def fix_broken_lines(text):
    """
    Reconstruct paragraphs WITHOUT deleting any information.
    - Joins broken lines
    - Preserves headings
    - Preserves bullet/number lists
    """

    lines = text.split("\n")
    final = []
    buffer = ""

    for line in lines:
        stripped = line.rstrip()

        if stripped == "":
            if buffer:
                final.append(buffer.strip())
                buffer = ""
            final.append("")
            continue

        # Heading detection
        if stripped.isupper() and len(stripped) > 5:
            if buffer:
                final.append(buffer.strip())
                buffer = ""
            final.append(stripped)
            continue

        # Bullet / numbered list detection
        if re.match(r"^(\d+\.\d+|\d+\.|[-•]\s)", stripped):
            if buffer:
                final.append(buffer.strip())
                buffer = ""
            final.append(stripped)
            continue

        # Sentence boundary check
        if buffer.endswith((".", "?", "!", ":")):
            final.append(buffer.strip())
            buffer = stripped
        else:
            buffer += " " + stripped if buffer else stripped

    if buffer:
        final.append(buffer.strip())

    return "\n".join(final)


def clean_extracted_text(text):

    text = text.replace("\r", "")

    # Remove weird unicode artifacts (safe)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = fix_broken_lines(text)

    return text.strip()