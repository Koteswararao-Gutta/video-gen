# config.py

import os
from dotenv import load_dotenv

load_dotenv()

# --- Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"  #" for a cheaper option

# --- Google TTS ---
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
TTS_VOICE = "en-US-Neural2-D"
TTS_LANGUAGE_CODE = "en-US"

# --- Pexels ---
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_PER_PAGE = 5

# --- Script ---
SCENE_COUNT = 5
MAX_WORDS_PER_SCENE = 20
MIN_WORDS_PER_SCENE = 10

# --- Paths ---
OUTPUT_DIR = "output"
AUDIO_DIR = "output/audio"
CLIPS_DIR = "output/clips"
FINAL_VIDEO = "output/final.mp4"
SUBTITLE_FILE = "output/subtitles.srt"

# --- Video ---
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
