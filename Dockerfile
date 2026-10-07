FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# System deps for librosa / soundfile / onnxruntime
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libsndfile1 \
        ffmpeg \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install piper-tts

# App code
COPY src/ ./src/
COPY app.py .
COPY scripts/ ./scripts/

# Download models at build time (they're gitignored)
RUN mkdir -p models/birdnet models/piper \
 && curl -L -o models/birdnet/model.onnx \
      "https://huggingface.co/tphakala/BirdNET-v2.4/resolve/main/BirdNET_v2.4_fp32_dfttrunc.onnx" \
 && curl -L -o models/birdnet/labels.txt \
      "https://huggingface.co/tphakala/BirdNET-v2.4/resolve/main/labels.txt" \
 && curl -L -o models/piper/en_US-lessac-medium.onnx \
      "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx" \
 && curl -L -o models/piper/en_US-lessac-medium.onnx.json \
      "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"

EXPOSE 7860

CMD ["python", "app.py"]
