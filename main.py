# main.py
import sys
import os
import json
import time

from core.script_gen import generate_script
from core.tts import generate_audio_for_scenes
from core.footage import get_footage_for_scenes
from core.subtitles import build_srt
from core.assembler import assemble
from config import (
    OUTPUT_DIR,
    AUDIO_DIR,
    CLIPS_DIR
)


def run_pipeline(topic: str) -> str:
    """
    Orchestrates the complete video generation pipeline.

    Runs all 5 modules in sequence: script generation, audio generation,
    footage fetching, subtitle building, and final assembly. Returns the
    path to the final video file.
    """
    # Record start time
    start_time = time.time()

    # Create all output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(CLIPS_DIR, exist_ok=True)

    # Print banner
    print("=" * 50)
    print("   Video Generator — Level 0 Pipeline")
    print("=" * 50)
    print(f"Topic: {topic}")
    print("=" * 50)

    # STEP 1 — Script Generation
    print("\n[1/5] Generating script...")

    script = generate_script(topic)
    scenes = script['scenes']

    # Save script to disk for debugging
    script_path = f"{OUTPUT_DIR}/script.json"
    with open(script_path, "w") as f:
        json.dump(script, f, indent=2)
    print(f"Script saved to: {script_path}")

    # STEP 2 — Audio Generation
    print("\n[2/5] Generating audio...")

    audio_data = generate_audio_for_scenes(scenes)

    # STEP 3 — Footage
    print("\n[3/5] Fetching footage...")

    footage_data = get_footage_for_scenes(scenes)

    # STEP 4 — Subtitles
    print("\n[4/5] Building subtitles...")

    subtitle_path = build_srt(audio_data, scenes)

    # STEP 5 — Assembly
    print("\n[5/5] Assembling video...")

    # Build scene_data by combining audio_data and footage_data
    scene_data = []
    for audio_item in audio_data:
        clip_item = next(
            f for f in footage_data
            if f['scene_id'] == audio_item['scene_id']
        )
        scene_data.append({
            "scene_id": audio_item['scene_id'],
            "clip_path": clip_item['clip_path'],
            "audio_path": audio_item['audio_path']
        })

    final_path = assemble(scene_data, subtitle_path)

    # Calculate elapsed time
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    # Print final summary
    print("\n" + "=" * 50)
    print("   Pipeline Complete!")
    print("=" * 50)
    print(f"Topic:      {topic}")
    print(f"Title:      {script['title']}")
    print(f"Scenes:     {len(scenes)}")
    print(f"Duration:   ~{len(scenes) * 5}s estimated")
    print(f"Time taken: {minutes}m {seconds}s")
    print(f"Output:     {final_path}")
    print("=" * 50)

    return final_path


if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        print("No topic provided.")
        print("Usage: python main.py 'your topic here'")
        sys.exit(1)

    try:
        final = run_pipeline(topic)
    except ValueError as e:
        print(f"\nPipeline error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "the water cycle"
        print(f"No topic provided.")
        print(f"Using default: '{topic}'")
        print(f"Usage: python main.py 'your topic here'")
        print()

    try:
        final = run_pipeline(topic)
    except ValueError as e:
        print(f"\nPipeline error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise
