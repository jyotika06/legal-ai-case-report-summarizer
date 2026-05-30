import { useState, useContext, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { DataContext } from "../context/DataContext";
import "../App.css";

function UploadPage() {
  const [mode, setMode] = useState("upload");
  const [file, setFile] = useState(null);
  const [voiceText, setVoiceText] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  const recognitionRef = useRef(null);

  const { setExtractedText } = useContext(DataContext);
  const navigate = useNavigate();

  // ===============================
  // PDF Upload Handler
  // ===============================
  const handleUpload = async () => {
    if (!file) return alert("Please select a judgment PDF");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!data.extractedText) {
      alert("Error extracting document text.");
      return;
    }

    setExtractedText(data.extractedText);
    navigate("/summary");
  };

  // ===============================
  // Speech Recognition
  // ===============================
  const startRecording = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.continuous = true;

    let finalTranscript = "";

    recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + " ";
        }
      }

      setVoiceText(cleanTranscript(finalTranscript.trim()));
    };

    recognition.onerror = (event) => {
      console.error("Speech error:", event.error);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.start();
    recognitionRef.current = recognition;
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const cleanTranscript = (text) => {
    return text.replace(/\b(\w+)( \1\b)+/gi, "$1");
  };

  const handleVoiceSubmit = () => {
    if (!voiceText.trim()) {
      alert("No voice input detected.");
      return;
    }

    setExtractedText(voiceText);
    navigate("/summary");
  };

  return (
    <div className="upload-wrapper">
      <div className="upload-card">

        <h2 className="upload-title">Upload Legal Document</h2>
        <p className="upload-sub">
          Upload a judgment PDF or speak case details to extract insights.
        </p>

        {/* Mode Toggle */}
        <div className="mode-toggle">
          <button
            className={mode === "upload" ? "active" : ""}
            onClick={() => setMode("upload")}
          >
            📄 Upload PDF
          </button>

          <button
            className={mode === "voice" ? "active" : ""}
            onClick={() => setMode("voice")}
          >
            🎙 Voice Input
          </button>
        </div>

        {/* ================= Upload Mode ================= */}
        {mode === "upload" && (
          <>
            <label className="upload-dropzone">
              <div className="upload-icon">⬆</div>
              <p>Click to browse or drag & drop PDF</p>

              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </label>

            {file && (
              <p className="selected-file">📄 {file.name}</p>
            )}

            <button className="btn primary-btn" onClick={handleUpload}>
              Upload & Extract →
            </button>
          </>
        )}

        {/* ================= Voice Mode ================= */}
        {mode === "voice" && (
          <div className="voice-section">
            <textarea
              value={voiceText}
              placeholder="Your spoken case details will appear here..."
              readOnly
            />

            {!isRecording ? (
              <button className="btn primary-btn" onClick={startRecording}>
                🎤 Start Recording
              </button>
            ) : (
              <button className="btn danger-btn" onClick={stopRecording}>
                ⏹ Stop Recording
              </button>
            )}

            <button className="btn primary-btn" onClick={handleVoiceSubmit}>
              Process Voice →
            </button>
          </div>
        )}

      </div>
    </div>
  );
}

export default UploadPage;