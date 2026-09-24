"""Post-processing of model generated text for SceneSpeak.

Implements Section 7.3 of the SceneSpeak PDR:
1. Strip markdown symbols (*, #, bullets, backticks, brackets) for clean speech TTS.
2. Cap output at 3 sentences and hard-cap at ~60 words.
3. Detect retake keywords (e.g., blurry, too dark) -> set retake = True.
4. Detect hazard keywords (e.g., stairs, vehicle, edge, obstacle) -> set hazard = True.
"""

import re
from typing import Tuple

# Keywords that indicate safety hazards or obstacles requiring caution
HAZARD_KEYWORDS = [
    "stair",
    "stairs",
    "step",
    "steps",
    "curb",
    "vehicle",
    "car",
    "truck",
    "bus",
    "traffic",
    "bike",
    "bicycle",
    "motorcycle",
    "edge",
    "drop-off",
    "wet floor",
    "puddle",
    "slick",
    "obstacle",
    "hazard",
    "construction",
    "hole",
    "trip",
    "wires",
    "low hanging",
]

# Keywords that indicate the photo was poor quality and should be retaken
RETAKE_KEYWORDS = [
    "blurry",
    "blurred",
    "too dark",
    "pitch black",
    "underexposed",
    "overexposed",
    "washed out",
    "unclear",
    "cannot make out",
    "cannot tell",
    "please retake",
    "retake the photo",
    "lens covered",
    "obstructed camera",
]


def strip_markdown(text: str) -> str:
    """Removes markdown formatting characters to prepare text for TTS audio."""
    if not text:
        return ""

    # Remove headers (#)
    cleaned = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Remove bullet markers (- or * or • at start of line)
    cleaned = re.sub(r"^\s*[-*•]\s*", "", cleaned, flags=re.MULTILINE)
    # Remove formatting characters (*, _, `, ~, [, ])
    cleaned = re.sub(r"[*_`~\[\]]", "", cleaned)
    # Fix spaces before punctuation (. , ! ?)
    cleaned = re.sub(r"\s+([.,!?])", r"\1", cleaned)
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def truncate_sentences_and_words(
    text: str,
    max_sentences: int = 3,
    max_words: int = 60,
) -> str:
    """Caps output at max_sentences (default 3) and hard caps at max_words (~60)."""
    if not text:
        return ""

    # Split on sentence boundaries (. ! ?)
    sentence_matches = re.split(r"(?<=[.!?])\s+", text)
    selected_sentences = sentence_matches[:max_sentences]
    truncated_text = " ".join(selected_sentences).strip()

    # Hard cap at max_words
    words = truncated_text.split()
    if len(words) > max_words:
        truncated_text = " ".join(words[:max_words])
        if not truncated_text.endswith((".", "!", "?")):
            truncated_text += "."

    return truncated_text


def detect_hazards(text: str) -> bool:
    """Returns True if any hazard/obstacle keyword is detected."""
    lower = text.lower()
    return any(re.search(rf"\b{re.escape(k)}\b", lower) for k in HAZARD_KEYWORDS)


def detect_retake(text: str) -> bool:
    """Returns True if any retake keyword is detected."""
    lower = text.lower()
    return any(k in lower for k in RETAKE_KEYWORDS)


def postprocess_response(raw_text: str) -> Tuple[str, bool, bool]:
    """Clean model output, detect hazard and retake flags.
    
    Returns:
        (cleaned_text, hazard_flag, retake_flag)
    """
    cleaned = strip_markdown(raw_text)
    truncated = truncate_sentences_and_words(cleaned, max_sentences=3, max_words=60)
    hazard = detect_hazards(truncated)
    retake = detect_retake(truncated)

    return truncated, hazard, retake
