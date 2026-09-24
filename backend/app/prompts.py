"""System prompt templates and prompt assembly for SceneSpeak.

These prompts reflect Section 8.2 and Section 10.2 of the SceneSpeak PDR:
- Audio-first, concise (<3 sentences)
- Hazard-first prioritization
- Honest hedging when unsure ("it looks like")
- Context enrichment (ambient signals & previous scene memory)
"""

from typing import Optional
from backend.app.schemas import ContextData, ModeEnum

# System prompt for Describe mode (Section 8.2)
PROMPT_DESCRIBE = (
    "You are the eyes of a blind person. Describe this photo for audio.\n"
    "- Maximum 3 short sentences. Plain spoken language. No markdown.\n"
    "- Mention hazards and obstacles first, then people, then layout.\n"
    "- Give positions as left, right, ahead, or clock positions.\n"
    "- Estimate distances roughly (for example 'about two steps away').\n"
    "- If unsure, say 'it looks like'. Never guess.\n"
    "- If the image is blurry, dark, or unclear, say so and ask the user to retake it."
)

# System prompt for Read mode (Section 8.2)
PROMPT_READ = (
    "Read all visible text in this photo exactly, in order. "
    "Use plain spoken language without markdown or bullet points. "
    "If there is no readable text, say 'No readable text found'."
)

# System prompt for Ask mode (Section 8.2)
PROMPT_ASK = (
    "You are an assistive visual guide for a visually impaired user. "
    "Answer the user's question about this image briefly and honestly in 1-2 spoken sentences. "
    "If the answer is not visible in the image, say you cannot tell."
)


def get_base_prompt(mode: ModeEnum) -> str:
    """Retrieve the base system prompt corresponding to the given mode."""
    if mode == ModeEnum.READ:
        return PROMPT_READ
    elif mode == ModeEnum.ASK:
        return PROMPT_ASK
    return PROMPT_DESCRIBE


def format_context_block(context: Optional[ContextData]) -> str:
    """Formats Ambient Information Signals (AIS) into a prompt context block.
    
    See PDR Section 10.2:
    Example:
    'Context: Time 21:40 (night). Heading 90° (east). Near "Main Street".
     Previous scene: "Closed door ahead."'
    """
    if not context:
        return ""

    parts = []
    if context.client_timestamp:
        parts.append(f"Time: {context.client_timestamp}")
    if context.compass_heading is not None:
        parts.append(f"Heading: {context.compass_heading:.0f}°")
    if context.location_hint:
        parts.append(f"Near: '{context.location_hint}'")

    context_str = ""
    if parts:
        context_str += "Ambient Context: " + ", ".join(parts) + "\n"

    if context.previous_scene_text:
        context_str += (
            f"Previous scene description: \"{context.previous_scene_text}\". "
            "Note any notable changes if relevant.\n"
        )

    return context_str.strip()


def assemble_prompt(
    mode: ModeEnum,
    question: Optional[str] = None,
    context: Optional[ContextData] = None,
) -> str:
    """Combine base prompt, optional ambient context, and question for VLM input."""
    base = get_base_prompt(mode)
    context_block = format_context_block(context)

    prompt_parts = [base]

    if context_block:
        prompt_parts.append(f"\n[Additional Context]\n{context_block}")

    if mode == ModeEnum.ASK and question:
        sanitized_question = question.strip()[:200]
        prompt_parts.append(f"\n[User Question]: \"{sanitized_question}\"")

    if context and context.language == "hi":
        prompt_parts.append("\n[Language Requirement]: Respond in simple, natural spoken Hindi (Devanagari script or conversational Hindi) suitable for text-to-speech.")

    return "\n".join(prompt_parts)
