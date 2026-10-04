import os
import subprocess
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve frontend static files
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

# Auto-downloads tiny model on first run
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")

# Groq client (free API)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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
        src = wav_path if result.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0 else tmp_path
        segments, _ = whisper_model.transcribe(src, beam_size=1, language="en", vad_filter=True)
        transcript = "".join(seg.text for seg in segments).strip()
    finally:
        os.remove(tmp_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

    return {"transcript": transcript}


SYSTEM_PROMPT = """Convert the transcript into a Markdown recipe. Output only the Markdown, nothing else.\n\nExample input:\nso you take two eggs and crack them into a bowl, add a pinch of salt, whisk it all together, then heat a pan with some butter and pour the eggs in, cook on low for about three minutes until set\n\nExample output:\n# Scrambled Eggs\n\n## Ingredients\n- 2 eggs\n- 1 pinch of salt\n- 1 teaspoon butter\n\n## Instructions\n1. Crack the eggs into a bowl and add a pinch of salt.\n2. Whisk the eggs together until combined.\n3. Heat a pan over low heat and melt the butter.\n4. Pour in the egg mixture and cook on low for about 3 minutes until just set.\n5. Serve immediately."""


@app.post("/format")
async def format_recipe(body: dict):
    transcript = body.get("transcript", "")
    try:
        message = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Free Groq model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return {"markdown": message.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
