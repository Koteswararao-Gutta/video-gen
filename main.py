# main.py
import sys
import os
import json
from pydub import AudioSegment

from config import (
    GEMINI_API_KEY, PEXELS_API_KEY, GOOGLE_APPLICATION_CREDENTIALS,
    AUDIO_DIR, CLIPS_DIR, OUTPUT_DIR
)
from core.script_gen import generate_script
from core.tts import generate_audio
from core.footage import get_footage
from core.subtitles import build_srt
from core.assembler import assemble


def main():
    """
    Orchestrate the complete video generation pipeline.
    
    Flow:
    1. Accept topic from command line or use default
    2. Generate script with scenes
    3. Generate audio narration for each scene
    4. Fetch stock footage for each scene
    5. Build SRT subtitle file
    6. Assemble final video with all components
    """
    # Validate environment
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY not set in .env file")
    if not PEXELS_API_KEY:
        raise EnvironmentError("PEXELS_API_KEY not set in .env file")
    if not GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        raise EnvironmentError(
            f"GOOGLE_APPLICATION_CREDENTIALS not set or file not found: {GOOGLE_APPLICATION_CREDENTIALS}"
        )
    
    # Get topic from command line or use default
    topic = sys.argv[1] if len(sys.argv) > 1 else "the water cycle"
    
    print("\n" + "="*70)
    print("VIDEO GENERATOR — LEVEL 0 PIPELINE")
    print("="*70 + "\n")
    
    try:
        # Create output directories
        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(CLIPS_DIR, exist_ok=True)
        
        # STEP 1: Script generation
        print("[1/5] Generating script...")
        script = generate_script(topic)
        title = script.get("title", "Unknown Title")
        scenes = script.get("scenes", [])
        print(f"      Title: {title}")
        print(f"      Scenes: {len(scenes)}")
        
        # Save script for debugging
        script_path = f"{OUTPUT_DIR}/script.json"
        with open(script_path, "w") as f:
            json.dump(script, f, indent=2)
        print(f"      Saved to: {script_path}\n")
        
        # STEP 2: Audio generation
        print("[2/5] Generating audio...")
        audio_data = []
        for scene in scenes:
            scene_id = scene["id"]
            narration = scene["narration"]
            audio_path = f"{AUDIO_DIR}/scene_{scene_id}.mp3"
            generate_audio(narration, audio_path)
            audio_data.append({
                "scene_id": scene_id,
                "audio_path": audio_path
            })
        print()
        
        # STEP 3: Footage fetching
        print("[3/5] Fetching footage...")
        clip_paths = []
        for scene in scenes:
            scene_id = scene["id"]
            keyword = scene["visual_keyword"]
            clip_path = f"{CLIPS_DIR}/scene_{scene_id}.mp4"
            get_footage(keyword, clip_path)
            clip_paths.append(clip_path)
        print()
        
        # STEP 4: Subtitle building
        print("[4/5] Building subtitles...")
        subtitle_path = build_srt(audio_data, scenes)
        print()
        
        # STEP 5: Assembly
        print("[5/5] Assembling video...")
        scene_data = []
        for i, scene in enumerate(scenes):
            audio_path = audio_data[i]["audio_path"]
            clip_path = clip_paths[i]
            
            # Get audio duration in seconds
            audio = AudioSegment.from_mp3(audio_path)
            duration_seconds = len(audio) / 1000.0
            
            scene_data.append({
                "scene_id": scene["id"],
                "clip_path": clip_path,
                "audio_path": audio_path
            })
        
        final_video = assemble(scene_data, subtitle_path)
        print()
        
        # Success!
        print("="*70)
        print("✓ DONE! Video saved to:")
        print(f"  {os.path.abspath(final_video)}")
        print("="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("✗ ERROR")
        print("="*70)
        print(f"Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
