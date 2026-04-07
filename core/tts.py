# core/tts.py

from google.cloud import texttospeech
import os
from config import (
    TTS_VOICE,
    TTS_LANGUAGE_CODE,
    AUDIO_DIR
)


def generate_audio(text: str, output_path: str) -> str:
    """Generate speech audio from text and save it to the specified output path."""
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=TTS_LANGUAGE_CODE,
        name=TTS_VOICE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(response.audio_content)

    return output_path


def generate_audio_for_scenes(scenes: list) -> list:
    """Generate audio for each scene and return metadata for generated files."""
    print(f"Generating audio for {len(scenes)} scenes...")
    results = []
    total = len(scenes)

    for scene in scenes:
        print(f"  [{scene['id']}/{total}] Generating audio: '{scene['narration'][:40]}...'")
        output_path = f"{AUDIO_DIR}/scene_{scene['id']}.mp3"
        generate_audio(scene['narration'], output_path)
        results.append({
            "scene_id": scene["id"],
            "audio_path": output_path,
            "narration": scene["narration"]
        })

    print(f"Audio generation complete. Files saved to: {AUDIO_DIR}/")
    return results


if __name__ == "__main__":
    os.makedirs("output/audio", exist_ok=True)

    test_scenes = [
        {
            "id": 1,
            "narration": (
                "Black holes form when massive "
                "stars collapse under their own gravity."
            ),
            "visual_keyword": "star explosion supernova"
        },
        {
            "id": 2,
            "narration": (
                "When a star runs out of fuel it can "
                "no longer resist gravitational collapse."
            ),
            "visual_keyword": "glowing star space"
        },
        {
            "id": 3,
            "narration": (
                "The core collapses forming a singularity "
                "with infinite density at its center."
            ),
            "visual_keyword": "black hole space orbit"
        },
        {
            "id": 4,
            "narration": (
                "Nothing can escape a black hole not "
                "even light itself beyond the event horizon."
            ),
            "visual_keyword": "dark space light bending"
        },
        {
            "id": 5,
            "narration": (
                "Scientists detect black holes by "
                "observing their gravitational effects on nearby matter."
            ),
            "visual_keyword": "telescope observatory night sky"
        }
    ]

    audio_data = generate_audio_for_scenes(test_scenes)

    print("\nResult summary:")
    for item in audio_data:
        exists = os.path.exists(item["audio_path"])
        size = os.path.getsize(item["audio_path"]) if exists else 0
        print(f"  scene_{item['scene_id']}.mp3 — exists: {exists}, size: {size} bytes")
