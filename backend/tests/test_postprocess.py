"""Unit tests for text postprocessing, hazard detection, and retake detection.

Corresponds to Section 15.4 of the SceneSpeak PDR.
"""

from backend.app.postprocess import (
    detect_hazards,
    detect_retake,
    postprocess_response,
    strip_markdown,
    truncate_sentences_and_words,
)


def test_strip_markdown():
    """Verify markdown symbols (*, #, _, backticks, bullets) are removed."""
    raw = "### Warning!\n- **Stairs** ahead `watch out`."
    cleaned = strip_markdown(raw)
    assert "*" not in cleaned
    assert "#" not in cleaned
    assert "`" not in cleaned
    assert "Stairs ahead watch out." in cleaned


def test_truncate_sentences():
    """Verify text is limited to at most 3 sentences."""
    long_text = "First sentence. Second sentence! Third sentence? Fourth sentence. Fifth sentence."
    truncated = truncate_sentences_and_words(long_text, max_sentences=3)
    assert "First sentence." in truncated
    assert "Second sentence!" in truncated
    assert "Third sentence?" in truncated
    assert "Fourth sentence." not in truncated


def test_hazard_detection():
    """Verify hazard keywords correctly toggle hazard flag."""
    assert detect_hazards("There are steep stairs directly ahead.") is True
    assert detect_hazards("A vehicle is approaching from your left.") is True
    assert detect_hazards("Watch out for a wet floor puddle.") is True
    assert detect_hazards("A clear table is ahead of you.") is False


def test_retake_detection():
    """Verify poor quality images trigger retake flag."""
    assert detect_retake("The photo is too dark to see anything clearly.") is True
    assert detect_retake("This image appears blurry, please retake.") is True
    assert detect_retake("A quiet hallway with closed doors.") is False


def test_postprocess_pipeline():
    """End-to-end check of postprocess_response helper."""
    raw = "**Caution**: Wet floor on your right. A chair is on your left. Move slowly."
    cleaned, hazard, retake = postprocess_response(raw)
    assert "**" not in cleaned
    assert hazard is True
    assert retake is False
