import os
import fitz
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Internal modules (Provider-agnostic)
from cleaner import clean_extracted_text
from entity_extraction_model import extract_entities
from summarization_model import summarize_text
from structured_legal_model import extract_structured_legal_info
from conversational_model import ask_legal_ai


# ----------------------------------------
# FLASK APP INITIALIZATION
# ----------------------------------------
app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------------------
# HEALTH CHECK
# ----------------------------------------
@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Legal AI Backend Running"
    }), 200


# ----------------------------------------
# UPLOAD PDF → CLEAN TEXT
# ----------------------------------------
@app.post("/upload")
def upload_pdf():

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty file name"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    raw_text = ""

    try:
        pdf = fitz.open(file_path)
        for page in pdf:
            raw_text += page.get_text()
        pdf.close()

    except Exception as e:
        return jsonify({
            "error": f"PDF parsing failed: {str(e)}"
        }), 500

    cleaned_text = clean_extracted_text(raw_text)

    return jsonify({
        "fileName": file.filename,
        "extractedText": cleaned_text
    }), 200


# ----------------------------------------
# LEGAL ENTITY EXTRACTION
# ----------------------------------------
@app.post("/extract_entities")
def extract_entities_route():

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    try:
        parsed = extract_entities(data["text"])
        return jsonify(parsed), 200

    except Exception as e:
        return jsonify({
            "error": f"Entity extraction failed: {str(e)}"
        }), 500


# ----------------------------------------
# SMART SUMMARY
# ----------------------------------------
@app.post("/summarize")
def summarize_route():

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    try:
        result = summarize_text(data["text"])
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": f"Summarization failed: {str(e)}"
        }), 500


# ----------------------------------------
# FULL STRUCTURED LEGAL INFORMATION
# ----------------------------------------
@app.post("/legal_info")
def legal_info_route():

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    try:
        info = extract_structured_legal_info(data["text"])
        return jsonify(info), 200

    except Exception as e:
        return jsonify({
            "error": f"Legal information extraction failed: {str(e)}"
        }), 500


# ----------------------------------------
# CONVERSATIONAL LEGAL ASSISTANT
# ----------------------------------------
@app.post("/chatbot")
def chatbot_route():

    data = request.get_json()

    if not data:
        return jsonify({"answer": "Invalid request format."}), 400

    question = data.get("question", "").strip()
    context = data.get("context", "").strip()

    if not question:
        return jsonify({"answer": "Please enter a valid question."}), 400

    try:
        answer = ask_legal_ai(question, context)
        return jsonify({"answer": answer}), 200

    except Exception as e:
        return jsonify({
            "answer": f"⚠ Unable to process request: {str(e)}"
        }), 500


# ----------------------------------------
# RUN SERVER
# ----------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)