# ────────────────────────────────────────────────────────────────
#   Anime-Dubbing-Alpha – reproducible image with:
#   • ffmpeg + libass        (hard-burn subtitles)
#   • espeak-ng              (Coqui phonemizer)
#   • whisper + cached model (no checksum clashes)
# ────────────────────────────────────────────────────────────────

FROM python:3.10-slim

# ── base system packages ───────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libass9 libass-dev \
        espeak-ng libespeak-ng1 \
        git \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ────────────────────────────────────────────────
COPY docker/requirements.txt /tmp/requirements.txt
# ensure whisper is listed; if not, pip will just ignore the duplicate
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir --upgrade --no-warn-script-location "openai-whisper==20231117"

# ── One-time download of Whisper-small (avoids checksum races) ─
RUN python - <<'PY'
import whisper, os, pathlib
cache = pathlib.Path.home() / ".cache" / "whisper"
cache.mkdir(parents=True, exist_ok=True)
whisper._download(whisper._MODELS["small"], str(cache), in_memory=False)
print("✓ Whisper-small cached at", cache)
PY

# ── copy code and expose app ───────────────────────────────────
WORKDIR /app
COPY . /app
EXPOSE 5000
CMD ["python", "-m", "anime_dubbing_alpha.webgui"]
