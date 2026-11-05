FROM python:3.12-slim
# ffmpeg cuts the clips; fonts for the captions; deno lets yt-dlp read YouTube's player code
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core curl unzip ca-certificates \
 && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh \
 && apt-get purge -y curl unzip && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# download the speech-to-text model once at build time, so uploads don't wait for it
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"
COPY . .
ENV PORT=8000 DATA_DIR=/tmp/cutcrew-jobs
CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
