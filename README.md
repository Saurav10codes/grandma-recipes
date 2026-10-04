
# Grandma Recipes 🍲

  

Speak a recipe → get it transcribed and formatted as Markdown. Runs **100% locally** (or free with Groq API).

  

## Stack

-  **Whisper tiny** (faster-whisper, CPU int8) — auto-downloads on first run (~75 MB)

-   **Ollama locally** for full offline mode

-  **FastAPI** backend

-  **React + Vite** frontend (neo-brutalism UI)

  

## Prerequisites

- Python 3.9+

- Node.js 18+

- FFmpeg: `sudo apt install ffmpeg`

  

### For local mode (no API calls):

- [Ollama](https://ollama.com) installed and running (`ollama serve`)

 

  

## Run Locally


  

### Backend

```bash

# Make sure Ollama is running: ollama serve

cd  backend

pip  install  -r  requirements.txt

uvicorn  main:app  --reload

```

  

### Frontend

```bash

cd  frontend

npm  install

npm  run  dev

```

  

Open http://localhost:5173

  

## Features

- 🎙 **Live recording** — click Record, speak, click Stop

- 📁 **File upload** — drag & drop or select audio files

- 📝 **Auto-formatting** — converts speech to structured Markdown recipes

- 🎨 **Neo-brutalism UI** — bold, minimalist design

- 🚀 **100% local** (optional) — no data leaves your machine

- ⚡ **Fast** — Whisper tiny on CPU, Groq API for formatting

  

## How it works

1. Record or upload audio

2. Whisper transcribes locally

3. LLM (Groq or Ollama) formats into Markdown recipe

4. Display with proper styling

  

## Environment Variables

-  `OLLAMA_URL` — defaults to `http://localhost:11434/api` for local Ollama

 
