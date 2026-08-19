# CPU-only, reproducible image for the Streamlit text-style analyzer.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PADDLEOCR_HOME=/opt/paddleocr

WORKDIR /app

# libgomp1 is needed by PaddlePaddle/OpenCV; libgl1 is used by OpenCV imports.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --prefer-binary -r requirements.txt

COPY text_style_analyzer/ ./text_style_analyzer/
COPY docker/model_warmup.py ./docker/model_warmup.py

# Bake Chinese PP-OCR detector, recognizer and angle-classifier models into the
# image. This makes the first request fast and avoids runtime model downloads.
RUN python docker/model_warmup.py

COPY app.py ./

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)" || exit 1

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
