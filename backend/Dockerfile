FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Deno: yt-dlp needs a JavaScript runtime to solve YouTube's challenges
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

WORKDIR /app
COPY requirements.txt .
# --pre pulls the newest nightly yt-dlp, which gets YouTube fixes first
RUN pip install --no-cache-dir -U -r requirements.txt \
    && pip install --no-cache-dir -U --pre "yt-dlp[default]"

COPY app.py .

CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 4 --timeout 900
