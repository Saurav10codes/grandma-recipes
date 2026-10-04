import os
import subprocess
import tempfile
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel

OLLAMA_URL = "http://localhost:11434/api"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve frontend static files
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

# Auto-downloads tiny model on first run
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")


MODEL = "qwen2.5:1.5b"


def ensure_ollama_model(model: str = MODEL):
    """Pull model if not already available locally."""
    try:
        models = requests.get(f"{OLLAMA_URL}/tags", timeout=5).json().get("models", [])
        if not any(m["name"].startswith(model) for m in models):
            requests.post(f"{OLLAMA_URL}/pull", json={"name": model}, timeout=300)
    except Exception:
        pass  # Ollama not running — will surface on /format call


ensure_ollama_model(MODEL)


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    suffix = os.path.splitext(audio.filename)[1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    wav_path = tmp_path + ".wav"
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path],
            capture_output=True, text=True
        )
        print("[ffmpeg stderr]", result.stderr[-800:])  # log last 800 chars
        print("[input size]", os.path.getsize(tmp_path), "[wav size]", os.path.getsize(wav_path) if os.path.exists(wav_path) else 0)

        src = wav_path if result.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0 else tmp_path
        segments, _ = whisper_model.transcribe(
            src,
            beam_size=1,
            language="en",
            vad_filter=True,
        )
        transcript = "".join(seg.text for seg in segments).strip()
        print("[transcript]", repr(transcript))
    finally:
        os.remove(tmp_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

    return {"transcript": transcript}


# Few-shot example teaches the model the exact pattern to copy.
# Small models (1B) follow examples far better than they follow rules.
SYSTEM_PROMPT = """Convert the transcript into a Markdown recipe. Output only the Markdown, nothing else.

Example input:
so you take two eggs and crack them into a bowl, add a pinch of salt, whisk it all together, then heat a pan with some butter and pour the eggs in, cook on low for about three minutes until set

Example output:
# Scrambled Eggs

## Ingredients
- 2 eggs
- 1 pinch of salt
- 1 teaspoon butter

## Instructions
1. Crack the eggs into a bowl and add a pinch of salt.
2. Whisk the eggs together until combined.
3. Heat a pan over low heat and melt the butter.
4. Pour in the egg mixture and cook on low for about 3 minutes until just set.
5. Serve immediately.
"""


@app.post("/format")
async def format_recipe(body: dict):
    transcript = body.get("transcript", "")
    # Ollama /api/chat supports system role; fall back to injected system prompt in /api/generate
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/chat",
            json={
                "model": MODEL,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": transcript},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        return {"markdown": resp.json()["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}
