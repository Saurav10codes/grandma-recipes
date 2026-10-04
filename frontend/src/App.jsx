import { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API = "https://grandma-recipes-7acq.onrender.com";

export default function App() {
  const [status, setStatus] = useState("idle"); // idle | recording | processing | done | error
  const [transcript, setTranscript] = useState("");
  const [recipe, setRecipe] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [showTranscript, setShowTranscript] = useState(false);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  async function processAudioBlob(blob, filename = "audio.wav") {
    setStatus("processing");
    setRecipe("");
    setTranscript("");
    setErrorMsg("");

    try {
      const form = new FormData();
      form.append("audio", blob, filename);

      const tRes = await fetch(`${API}/transcribe`, { method: "POST", body: form });
      const { transcript: t, error: tErr } = await tRes.json();
      if (tErr) throw new Error(tErr);
      setTranscript(t);

      const fRes = await fetch(`${API}/format`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript: t }),
      });
      const { markdown, error: fErr } = await fRes.json();
      if (fErr) throw new Error(fErr);
      setRecipe(markdown);
      setStatus("done");
    } catch (e) {
      setErrorMsg(e.message);
      setStatus("error");
    }
  }

  function startRecording() {
    chunksRef.current = [];
    navigator.mediaDevices
      .getUserMedia({ audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true } })
      .then((stream) => {
        // Pick the most whisper-friendly format the browser supports
        const mimeType = ["audio/wav", "audio/webm;codecs=pcm", "audio/webm"]
          .find((m) => MediaRecorder.isTypeSupported(m)) || "";

        const mr = new MediaRecorder(stream, mimeType ? { mimeType } : {});
        mediaRecorderRef.current = mr;

        mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
        mr.onstop = () => {
          stream.getTracks().forEach((t) => t.stop());
          const type = mr.mimeType || "audio/webm";
          const ext = type.includes("wav") ? "wav" : "webm";
          const blob = new Blob(chunksRef.current, { type });
          processAudioBlob(blob, `recording.${ext}`);
        };

        mr.start(100);
        setStatus("recording");
      })
      .catch((e) => { setErrorMsg(e.message); setStatus("error"); });
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
  }

  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (file) processAudioBlob(file, file.name);
    e.target.value = "";
  }

  const isRecording = status === "recording";
  const isProcessing = status === "processing";

  return (
    <div className="page">
      <header>
        <span className="logo">🍲</span>
        <h1>Grandma Recipes</h1>
        <p className="subtitle">Speak a recipe. Get it structured. Runs 100% locally.</p>
      </header>

      <main>
        <div className="card input-card">
          <div className="input-row">
            <button
              className={`btn-record ${isRecording ? "recording" : ""}`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isProcessing}
            >
              {isRecording ? "⏹ Stop Recording" : "🎙 Record"}
            </button>

            <label className="btn-upload" data-disabled={isProcessing}>
              📁 Upload Audio
              <input
                type="file"
                accept=".mp3,.wav,.m4a,.webm,.ogg"
                onChange={handleFileUpload}
                disabled={isProcessing || isRecording}
                hidden
              />
            </label>
          </div>

          {isRecording && (
            <div className="recording-indicator">
              <span className="dot" /> Recording… click Stop when done
            </div>
          )}

          {isProcessing && (
            <div className="status-bar">
              <span className="spinner" /> Processing locally, please wait…
            </div>
          )}

          {status === "error" && (
            <div className="error-bar">⚠ {errorMsg}</div>
          )}
        </div>

        {transcript && (
          <div className="card transcript-card">
            <button className="toggle-btn" onClick={() => setShowTranscript((v) => !v)}>
              {showTranscript ? "▲ Hide" : "▼ Show"} Raw Transcript
            </button>
            {showTranscript && <p className="transcript-text">{transcript}</p>}
          </div>
        )}

        {recipe && (
          <div className="card recipe-card">
            <div className="recipe">
              <ReactMarkdown>{recipe}</ReactMarkdown>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
