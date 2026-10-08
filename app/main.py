"""
main.py — a small Python web application built with FastAPI.

What it does:
  GET  /          -> the HTTPS front page of your website (HTML, see app/static/index.html)
  POST /api/mood  -> receives text, runs an AI sentiment model, returns POSITIVE/NEGATIVE
  GET  /ping      -> health check (Runpod Serverless load balancers call this)

Run locally:   uvicorn app.main:app --host 0.0.0.0 --port 8000
Then open:     http://localhost:8000
"""

import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Mood Checker", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# The model is loaded once, when the first request needs it, then kept in memory.
_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        from transformers import pipeline  # imported here so the web page loads instantly

        _classifier = pipeline("sentiment-analysis", model=MODEL_NAME, device=-1)  # -1 = CPU
    return _classifier


class MoodRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/ping")
def ping():
    return {"status": "healthy"}


@app.post("/api/mood")
def mood(req: MoodRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Please type some text.")
    start = time.perf_counter()
    result = get_classifier()(text)[0]
    return JSONResponse(
        {
            "label": result["label"],
            "confidence": round(float(result["score"]), 4),
            "milliseconds": round((time.perf_counter() - start) * 1000),
        }
    )


@app.on_event("startup")
def warm_up():
    # Load the model while the server starts so the first visitor doesn't wait.
    if os.getenv("SKIP_WARMUP") != "1":
        get_classifier()
