# Video Generation Pipeline — Level 0

A complete Python pipeline that transforms a topic into a fully-produced MP4 video with:
- AI-generated script (using Gemini)
- Neural text-to-speech narration (Google Cloud TTS)
- Stock video footage (Pexels API)
- Burned-in subtitles synced to audio
- Professional video assembly (FFmpeg)

## Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **FFmpeg** installed and available in your system PATH
  - Windows: `choco install ffmpeg` or download from https://ffmpeg.org/download.html
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
- **API Keys** (free tier available for all):
  - Google Gemini API key
  - Google Cloud Text-to-Speech credentials JSON
  - Pexels API key

### 2. Installation

```bash
# Clone or navigate to the project directory
cd video-gen

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Edit .env with your actual credentials
```

**Getting API Keys:**

**Gemini API:**
1. Go to https://aistudio.google.com/app/apikeys
2. Click "Create API Key"
3. Copy the key to `GEMINI_API_KEY` in `.env`

**Google Cloud Text-to-Speech:**
1. Create a Google Cloud project
2. Enable Text-to-Speech API
3. Create a service account and download the JSON key
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of this JSON file

**Pexels API:**
1. Go to https://www.pexels.com/api/
2. Sign up and copy your API key
3. Add to `PEXELS_API_KEY` in `.env`

### 4. Run the Pipeline

**With default topic (water cycle):**
```bash
python main.py
```

**With custom topic:**
```bash
python main.py "how black holes form"
```

The pipeline will:
1. Generate a 5-scene script from your topic
2. Create MP3 narration for each scene
3. Download matching stock footage
4. Build an SRT subtitle file
5. Assemble everything into `output/final.mp4`

## Project Structure

```
video-gen/
├── core/
│   ├── script_gen.py      # Gemini script generation
│   ├── tts.py             # Google Cloud Text-to-Speech
│   ├── footage.py         # Pexels video download
│   ├── subtitles.py       # SRT subtitle building
│   └── assembler.py       # FFmpeg video assembly
├── agents/                # Reserved for Level 1+
├── memory/                # Reserved for Level 1+
├── output/
│   ├── audio/             # Generated MP3 files
│   ├── clips/             # Downloaded video clips
│   ├── script.json        # Generated script (debug)
│   ├── subtitles.srt      # Subtitle file
│   └── final.mp4          # Final output video
├── config.py              # All settings (no hardcoding)
├── main.py                # Pipeline orchestrator
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

## Output Files

After running, the `output/` directory contains:

- **`final.mp4`** — The final video (watch this!)
- **`script.json`** — The AI-generated script (debugging)
- **`subtitles.srt`** — Subtitle file
- **`audio/`** — Individual scene MP3 narrations
- **`clips/`** — Individual scene video clips

## Configuration

All settings are in `config.py`. Key tuning options:

```python
SCENE_COUNT = 5              # Number of scenes (default: 5)
MAX_WORDS_PER_SCENE = 20     # Narration length (default: 20)
MIN_WORDS_PER_SCENE = 10     # Narration minimum (default: 10)

VIDEO_WIDTH = 1920           # Output resolution
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30               # Frames per second
```

## Troubleshooting

**"No footage found for: [keyword]"**
- The Pexels search didn't return results for the visual keyword
- Try a different topic or adjust PEXELS_PER_PAGE in config.py

**"Failed to parse Gemini response as JSON"**
- Gemini occasionally returns unexpected format
- Try running again (temporary API issue)

**FFmpeg errors**
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check your PATH environment variable

**"GOOGLE_APPLICATION_CREDENTIALS not found"**
- Verify the path to your Google Cloud service account JSON
- Use absolute paths in .env if relative paths don't work

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Script | Google Gemini 1.5 Flash | AI script generation |
| TTS | Google Cloud Text-to-Speech | Neural voice narration |
| Video | Pexels API | Stock footage download |
| Subtitles | pydub + srt | Audio-synced timing |
| Assembly | FFmpeg + ffmpeg-python | Video composition |
| Config | python-dotenv | Environment management |

## Future Levels

This is **Level 0** of a multi-level system:

- **Level 1:** Agent-based scene variation and dynamic content
- **Level 2:** Parallel processing and task coordination
- **Level 3:** Learning systems and adaptive optimization

Reserved packages: `agents/` and `memory/`

## Performance Notes

- First run downloads dependencies: ~2-3 minutes for all installation + API calls
- Script generation: ~10-20 seconds
- Audio generation: ~5-10 seconds per scene
- Footage download: ~20-60 seconds per scene (depends on file sizes)
- Video assembly: ~1-3 minutes (FFmpeg encoding)

**Total first run: ~5-10 minutes** (varies by topic and connection)

## License & Support

This is a complete, production-ready pipeline. Modify as needed for your use case.

For issues with:
- **Gemini:** https://github.com/google/generative-ai-python
- **Google Cloud TTS:** https://cloud.google.com/python/docs/reference/texttospeech
- **Pexels API:** https://www.pexels.com/api/documentation/
- **FFmpeg:** https://ffmpeg.org/documentation.html
