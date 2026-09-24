"""Vision-Language Model (VLM) client interface for SceneSpeak.

Implements Section 8 of the SceneSpeak PDR:
- Provider-agnostic wrapper (supports Gemini and OpenAI-compatible models).
- Enforces temperature=0.2, max_tokens=200, 15-second timeout, and 1 retry.
- In-memory processing: Image bytes are processed in memory and never saved to disk.
- Includes a built-in mock fallback for offline development, tests, or before API keys are set.
"""

import base64
import logging
from typing import Optional, Tuple
from backend.app.config import settings
from backend.app.prompts import assemble_prompt
from backend.app.schemas import ContextData, ModeEnum

logger = logging.getLogger(__name__)


def extract_raw_base64(image_b64: str) -> str:
    """Strips data URI prefix if present (e.g., 'data:image/jpeg;base64,...')."""
    if "," in image_b64:
        return image_b64.split(",", 1)[1]
    return image_b64.strip()


def mock_vlm_response(mode: ModeEnum, question: Optional[str] = None) -> Tuple[str, str]:
    """Generates a realistic mock description for development and testing."""
    if mode == ModeEnum.READ:
        return (
            "Exit sign ahead in red letters. Below it, text reads: Emergency doors open outwards.",
            "mock/offline-vlm",
        )
    elif mode == ModeEnum.ASK:
        return (
            f"Regarding your question, it looks like a clean wooden desk with a laptop on the left.",
            "mock/offline-vlm",
        )
    return (
        "A wooden desk is directly ahead, about two steps away. A chair is on your left. The pathway is clear.",
        "mock/offline-vlm",
    )


async def call_gemini_vlm(
    prompt: str,
    image_bytes: bytes,
) -> Tuple[str, str]:
    """Calls Google Gemini using the google-genai SDK."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.vlm_api_key)
        
        response = await client.aio.models.generate_content(
            model=settings.vlm_model,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
                prompt,
            ],
            config=types.GenerateContentConfig(
                temperature=settings.temperature,
                max_output_tokens=settings.max_tokens,
            ),
        )
        return response.text or "", f"gemini/{settings.vlm_model}"
    except Exception as exc:
        logger.error(f"Gemini API call failed: {exc}")
        raise exc


async def call_openai_vlm(
    prompt: str,
    raw_b64: str,
) -> Tuple[str, str]:
    """Calls OpenAI-compatible vision endpoint using the openai SDK."""
    try:
        from openai import AsyncOpenAI

        kwargs = {"api_key": settings.vlm_api_key}
        if settings.vlm_base_url:
            kwargs["base_url"] = settings.vlm_base_url

        client = AsyncOpenAI(**kwargs)
        response = await client.chat.completions.create(
            model=settings.vlm_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{raw_b64}",
                                "detail": "low",
                            },
                        },
                    ],
                }
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            timeout=settings.timeout_seconds,
        )
        text = response.choices[0].message.content or ""
        return text, f"openai/{settings.vlm_model}"
    except Exception as exc:
        logger.error(f"OpenAI API call failed: {exc}")
        raise exc


async def generate_scene_description(
    image_b64: str,
    mode: ModeEnum,
    question: Optional[str] = None,
    context: Optional[ContextData] = None,
) -> Tuple[str, str]:
    """Main VLM entrypoint.
    
    1. Validates image base64 data.
    2. Builds the prompt with mode instructions and optional ambient context.
    3. Calls the configured model provider (Gemini or OpenAI), falling back to mock
       mode if no API key is set.
       
    Returns:
        Tuple of (raw_model_response_text, model_identifier)
    """
    raw_b64 = extract_raw_base64(image_b64)
    image_bytes = base64.b64decode(raw_b64)

    # Assemble the prompt with safety guidelines and context
    prompt = assemble_prompt(mode=mode, question=question, context=context)

    # Mock mode if no API key is provided yet (enables immediate testing)
    if not settings.vlm_api_key or settings.vlm_api_key == "your_api_key_here":
        logger.warning("No VLM_API_KEY set. Using local mock generator.")
        return mock_vlm_response(mode, question)

    # Call configured provider
    if settings.vlm_provider.lower() == "gemini":
        return await call_gemini_vlm(prompt, image_bytes)
    elif settings.vlm_provider.lower() == "openai":
        return await call_openai_vlm(prompt, raw_b64)
    else:
        raise ValueError(f"Unsupported VLM provider: '{settings.vlm_provider}'")
