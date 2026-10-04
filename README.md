# Grandma Recipes 🍲

Speak a recipe → get it transcribed and formatted as Markdown. Runs **100% locally**.

## Stack
- **Whisper tiny** (faster-whisper, CPU int8) — auto-downloads on first run
- **TinyLlama** via Ollama — auto-pulled on first run
- **FastAPI** backend
- **React + Vite** frontend (neo-brutalism UI)

## Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com) installed and running (`ollama serve`)
- Node.js 18+

## Run

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
> Whisper tiny (~75 MB) downloads automatically on first start.  
> TinyLlama (~600 MB) is pulled from Ollama automatically if not present.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173
