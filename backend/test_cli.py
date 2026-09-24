"""Single-image CLI test tool for SceneSpeak.

Implements PDR Section 11.4 Step 1:
"Script that sends one image to the model and prints the result."

Usage:
    python backend/test_cli.py --image eval/images/hazard_stairs.jpg --mode describe
    python backend/test_cli.py --image eval/images/text_sign.jpg --mode read
    python backend/test_cli.py --image eval/images/clean_room.jpg --mode ask --question "Is there a chair?"
"""

import argparse
import asyncio
import base64
import sys
import time
from pathlib import Path

# Add project root to sys.path so backend modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.postprocess import postprocess_response
from backend.app.schemas import ModeEnum
from backend.app.vlm import generate_scene_description


def load_image_as_base64(image_path: Path) -> str:
    """Reads an image file and converts it to base64 string."""
    if not image_path.exists():
        print(f"Error: Image file '{image_path}' not found.")
        sys.exit(1)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return base64.b64encode(image_bytes).decode("utf-8")


async def test_image(
    image_path: Path,
    mode_str: str,
    question: str = None,
):
    """Executes the SceneSpeak VLM pipeline on a single image file."""
    print("=" * 60)
    print("SceneSpeak CLI Test Runner")
    print("=" * 60)
    print(f"Image:    {image_path.name}")
    print(f"Mode:     {mode_str}")
    if question:
        print(f"Question: \"{question}\"")
    print("-" * 60)

    try:
        mode = ModeEnum(mode_str.lower())
    except ValueError:
        print(f"Error: Invalid mode '{mode_str}'. Choose from: describe, read, ask")
        sys.exit(1)

    image_b64 = load_image_as_base64(image_path)
    start_time = time.time()

    print("Sending image to VLM...")
    raw_text, model_name = await generate_scene_description(
        image_b64=image_b64,
        mode=mode,
        question=question,
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    # Post-process
    cleaned_text, hazard, retake = postprocess_response(raw_text)

    print("\n[Results]")
    print(f"Model:          {model_name}")
    print(f"Latency:        {elapsed_ms} ms")
    print(f"Hazard Alert:   {'[YES - HAZARD]' if hazard else 'No'}")
    print(f"Retake Advised: {'[YES - RETAKE]' if retake else 'No'}")
    print(f"\nSpeakable Text:\n\"{cleaned_text}\"")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Test SceneSpeak on a single image.")
    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to the image file (JPEG or PNG).",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="describe",
        choices=["describe", "read", "ask"],
        help="Operating mode: describe, read, or ask.",
    )
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="Spoken question for 'ask' mode.",
    )

    args = parser.parse_args()
    asyncio.run(test_image(args.image, args.mode, args.question))


if __name__ == "__main__":
    main()
