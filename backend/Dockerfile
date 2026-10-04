# Use a lightweight Python image
FROM python:3.11-slim

# Install ffmpeg for audio processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the Groq requirements and install them
COPY requirements-groq.txt .
RUN pip install --no-cache-dir -r requirements-groq.txt

# Copy your backend code
COPY . .

# Run the Groq version of the API
CMD ["uvicorn", "main-groq:app", "--host", "0.0.0.0", "--port", "10000"]