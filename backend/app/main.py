"""FastAPI application entrypoint for SceneSpeak.

Implements Section 11 and Section 14 of the SceneSpeak PDR:
- One service, one deploy: backend can serve frontend static files.
- /api/health: health check endpoint.
- /api/describe: core scene description endpoint (Describe, Read, Ask).
- /api/feedback: user rating and feedback collection.
- /api/stats: aggregated metrics for evaluation.
- Audible, graceful error responses so the client can speak errors aloud.
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.db import get_stats, init_db, log_feedback, log_scene
from backend.app.postprocess import postprocess_response
from backend.app.schemas import (
    DescribeRequest,
    DescribeResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    StatsResponse,
)
from backend.app.vlm import extract_raw_base64, generate_scene_description

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scenespeak")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes SQLite database tables on startup."""
    logger.info("Initializing SceneSpeak database...")
    init_db()
    logger.info("Database initialized.")
    yield


app = FastAPI(
    title="SceneSpeak API",
    description="Assistive scene description API for visually impaired users.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend uptime."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/api/describe", response_model=DescribeResponse, tags=["Vision"])
async def describe_scene(payload: DescribeRequest):
    """Process an image and generate a safety-aware spoken description.
    
    1. Validates payload size (must be <= MAX_IMAGE_BYTES).
    2. Sends frame to the configured Vision-Language Model.
    3. Postprocesses model text (strips markdown, caps length, flags hazards/retakes).
    4. Logs metadata to SQLite (privacy: no images stored).
    5. Returns speakable text and flags.
    """
    start_time = time.time()
    request_id = uuid.uuid4().hex[:8]

    # Validate image payload size
    raw_b64 = extract_raw_base64(payload.image_b64)
    estimated_bytes = len(raw_b64) * 3 // 4
    if estimated_bytes > settings.max_image_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail={
                "error": "Image payload exceeds limit",
                "spoken": "The photo is too large to process. Please try taking another photo.",
            },
        )

    try:
        # Call VLM
        raw_text, model_name = await generate_scene_description(
            image_b64=payload.image_b64,
            mode=payload.mode,
            question=payload.question,
            context=payload.context,
        )

        # Postprocess: clean text, detect hazards, detect retake signals
        cleaned_text, hazard, retake = postprocess_response(raw_text)

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Log metadata to SQLite (no images)
        log_scene(
            request_id=request_id,
            mode=payload.mode.value,
            response_text=cleaned_text,
            hazard=hazard,
            retake=retake,
            latency_ms=elapsed_ms,
            model=model_name,
        )

        return DescribeResponse(
            request_id=request_id,
            mode=payload.mode.value,
            text=cleaned_text,
            hazard=hazard,
            retake=retake,
            latency_ms=elapsed_ms,
            model=model_name,
        )

    except Exception as exc:
        logger.error(f"Error processing describe request: {exc}", exc_info=True)
        # Speakable failure response
        return JSONResponse(
            status_code=500,
            content={
                "request_id": request_id,
                "error": str(exc),
                "spoken": "Sorry, I had trouble processing that scene. Please tap to try again.",
            },
        )


@app.post("/api/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(payload: FeedbackRequest):
    """Log user rating (1-5 stars) and optional feedback note for a scene."""
    try:
        log_feedback(
            scene_id=payload.request_id,
            rating=payload.rating,
            note=payload.note,
        )
        return FeedbackResponse(ok=True, message="Feedback saved successfully")
    except Exception as exc:
        logger.error(f"Error saving feedback: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/stats", response_model=StatsResponse, tags=["Stats"])
async def get_system_stats():
    """Retrieve aggregate metrics for evaluation slides."""
    stats = get_stats()
    return StatsResponse(**stats)


# Serve frontend static files if directory exists
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists() and (frontend_dir / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
