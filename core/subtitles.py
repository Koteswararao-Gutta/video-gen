# core/subtitles.py

from pydub import AudioSegment
import srt
import datetime
import os
from config import SUBTITLE_FILE, AUDIO_DIR

def get_audio_duration(audio_path: str) -> float:
    """Get the duration of an audio file in seconds."""
    audio = AudioSegment.from_mp3(audio_path)
    return len(audio) / 1000.0

def build_srt(audio_data: list, scenes: list) -> str:
    """Build SRT subtitles from audio data and scenes."""
    cursor = 0.0
    subtitles = []
    print(f"Building subtitles for {len(audio_data)} scenes...")
    for item in audio_data:
        duration = get_audio_duration(item['audio_path'])
        narration = next(
            s['narration'] for s in scenes 
            if s['id'] == item['scene_id']
        )
        subtitle = srt.Subtitle(
            index=item['scene_id'],
            start=datetime.timedelta(seconds=cursor),
            end=datetime.timedelta(seconds=cursor + duration),
            content=narration
        )
        subtitles.append(subtitle)
        print(f"  Scene {item['scene_id']}: {cursor:.2f}s --> {cursor + duration:.2f}s ({duration:.2f}s)")
        cursor += duration
    composed = srt.compose(subtitles)
    with open(SUBTITLE_FILE, "w", encoding="utf-8") as f:
        f.write(composed)
    print(f"Subtitles written to: {SUBTITLE_FILE}")
    print(f"Total video duration: {cursor:.2f} seconds")
    return SUBTITLE_FILE

if __name__ == "__main__":
    test_audio_data = [
        {
            "scene_id": 1,
            "audio_path": "output/audio/scene_1.mp3",
            "narration": "Black holes form when massive stars collapse under their own gravity."
        },
        {
            "scene_id": 2,
            "audio_path": "output/audio/scene_2.mp3",
            "narration": "When a star runs out of fuel it can no longer resist gravitational collapse."
        },
        {
            "scene_id": 3,
            "audio_path": "output/audio/scene_3.mp3",
            "narration": "The core collapses forming a singularity with infinite density at its center."
        },
        {
            "scene_id": 4,
            "audio_path": "output/audio/scene_4.mp3",
            "narration": "Nothing can escape a black hole not even light itself beyond the event horizon."
        },
        {
            "scene_id": 5,
            "audio_path": "output/audio/scene_5.mp3",
            "narration": "Scientists detect black holes by observing their gravitational effects on nearby matter."
        }
    ]

    test_scenes = [
        {
            "id": 1,
            "narration": "Black holes form when massive stars collapse under their own gravity.",
            "visual_keyword": "star explosion supernova"
        },
        {
            "id": 2,
            "narration": "When a star runs out of fuel it can no longer resist gravitational collapse.",
            "visual_keyword": "glowing star space"
        },
        {
            "id": 3,
            "narration": "The core collapses forming a singularity with infinite density at its center.",
            "visual_keyword": "black hole space orbit"
        },
        {
            "id": 4,
            "narration": "Nothing can escape a black hole not even light itself beyond the event horizon.",
            "visual_keyword": "dark space light bending"
        },
        {
            "id": 5,
            "narration": "Scientists detect black holes by observing their gravitational effects on nearby matter.",
            "visual_keyword": "telescope observatory night sky"
        }
    ]

    subtitle_path = build_srt(test_audio_data, test_scenes)

    print("\nResult summary:")
    exists = os.path.exists(subtitle_path)
    print(f"  File exists: {exists}")
    if exists:
        with open(subtitle_path, "r") as f:
            print("\n--- SRT FILE CONTENT ---")
            print(f.read())
            print("------------------------")
