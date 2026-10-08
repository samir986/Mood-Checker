# Dockerfile — the recipe for the container image. GitHub builds it for you (see .github/workflows).

# Small official Python image (no GPU needed for this app).
FROM python:3.11-slim

WORKDIR /srv

# CPU-only PyTorch keeps the image ~4x smaller than the GPU version.
RUN pip install --no-cache-dir torch==2.4.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the AI model during the build so the website starts quickly.
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"

COPY app ./app

# The port the website listens on. Runpod Pods: expose 8000. Runpod Serverless sets PORT itself.
ENV PORT=8000
EXPOSE 8000

# 0.0.0.0 = accept connections from outside the container (required by Runpod).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
