"""Pydantic schemas and data contracts for SceneSpeak.

These schemas define the exact structure of incoming requests and outgoing
responses as specified in Section 9.1 and Section 14.1 of the SceneSpeak PDR.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ModeEnum(str, Enum):
    """The three operating modes supported by SceneSpeak."""
    DESCRIBE = "describe"
    READ = "read"
    ASK = "ask"


class ContextData(BaseModel):
    """Optional Ambient Information Signals (AIS) sent by the phone client.
    
    See PDR Section 10 for details.
    """
    compass_heading: Optional[float] = Field(
        None, description="Compass heading in degrees (0-360)."
    )
    client_timestamp: Optional[str] = Field(
        None, description="ISO 8601 timestamp from device clock."
    )
    location_hint: Optional[str] = Field(
        None, description="Coarse location description (e.g. street name). Never raw GPS coordinates."
    )
    previous_scene_text: Optional[str] = Field(
        None, description="Last describe result stored in device memory to detect changes."
    )
    language: Optional[str] = Field(
        "en", description="Target spoken language code: 'en' for English, 'hi' for Hindi."
    )


class DescribeRequest(BaseModel):
    """Request payload sent from phone frontend to POST /api/describe."""
    image_b64: str = Field(
        ...,
        description="Base64 encoded JPEG image (max 768px on longest side, quality ~0.7)."
    )
    mode: ModeEnum = Field(
        default=ModeEnum.DESCRIBE,
        description="Operation mode: 'describe', 'read', or 'ask'."
    )
    question: Optional[str] = Field(
        default=None,
        max_length=200,
        description="User's spoken question for 'ask' mode (transcribed via Web Speech STT)."
    )
    context: Optional[ContextData] = Field(
        default=None,
        description="Optional ambient sensor signals to ground the description."
    )


class DescribeResponse(BaseModel):
    """Contract response returned by POST /api/describe (PDR Section 9.1)."""
    request_id: str = Field(..., description="Unique trace ID for logging and feedback.")
    mode: str = Field(..., description="The mode that was processed.")
    text: str = Field(..., description="Cleaned, speakable response suitable for audio TTS.")
    hazard: bool = Field(
        default=False,
        description="True if an immediate obstacle or danger was detected."
    )
    retake: bool = Field(
        default=False,
        description="True if the image was blurry, too dark, or unusable."
    )
    latency_ms: int = Field(..., description="End-to-end processing latency in milliseconds.")
    model: str = Field(..., description="Name and provider of the model that generated the output.")


class FeedbackRequest(BaseModel):
    """Request payload for POST /api/feedback (PDR Section 13.2 & 14.1)."""
    request_id: str = Field(..., description="ID of the scene being reviewed.")
    rating: int = Field(..., ge=1, le=5, description="Score from 1 (poor) to 5 (great).")
    note: Optional[str] = Field(None, max_length=500, description="Optional text feedback.")


class FeedbackResponse(BaseModel):
    """Response returned after recording user feedback."""
    ok: bool = True
    message: str = "Feedback recorded successfully"


class StatsResponse(BaseModel):
    """Aggregated metrics returned by GET /api/stats for evaluation and slides."""
    total_requests: int
    avg_latency_ms: float
    retake_rate: float
    hazard_rate: float


class HealthResponse(BaseModel):
    """Response returned by GET /api/health."""
    status: str = "ok"
    version: str = "1.0.0"
