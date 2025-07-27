# Multi-stage build for optimization and AMD64 compatibility
FROM --platform=linux/amd64 python:3.10-slim-bullseye AS builder

WORKDIR /app

# Install dependencies (CPU-only, AMD64-compatible, including rake-nltk)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir \
    pymupdf \
    sentence-transformers \
    nltk \
    scikit-learn \
    rake-nltk \
    torch --index-url https://download.pytorch.org/whl/cpu

# Pre-download NLTK data and model during build (now including 'stopwords' for RAKE)
RUN python -c "import nltk; \
    nltk.download('punkt', quiet=True); \
    nltk.download('stopwords', quiet=True)" && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Final stage: Copy from builder and set up runtime
FROM --platform=linux/amd64 python:3.10-slim-bullseye

WORKDIR /app

# Copy installed packages and pre-downloaded data from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /root/nltk_data /root/nltk_data
COPY --from=builder /root/.cache /root/.cache

# Copy your application code
COPY main.py .

# Entry point: Pass docs, persona, job as args (same as before)
ENTRYPOINT ["python", "main.py"]
