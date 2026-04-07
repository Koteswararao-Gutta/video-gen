# core/script_gen.py

from google import genai
import json
from config import GEMINI_API_KEY, GEMINI_MODEL, SCENE_COUNT


def generate_script(topic: str) -> dict:
    """
    Generate a structured video script for the given topic using Google Gemini API.
    
    Args:
        topic: The subject of the video script to generate
        
    Returns:
        A dictionary with 'title' and 'scenes' keys, where each scene contains
        'id', 'narration', and 'visual_keyword' fields
        
    Raises:
        ValueError: If JSON parsing fails or structure validation fails
    """
    print(f"Generating script for topic: '{topic}'")
    
    prompt = f"""
        You are a video script writer.
        Create a short educational video script about: {topic}

        Return ONLY valid JSON. No markdown. No explanation. 
        No code blocks. Just the raw JSON object.

        Use exactly this structure:
        {{
        "title": "video title here",
        "scenes": [
            {{
            "id": 1,
            "narration": "10 to 20 words the narrator speaks",
            "visual_keyword": "4 to 5 word concrete searchable stock footage term"
            }}
        ]
        }}

        Rules:
        - Exactly {SCENE_COUNT} scenes
        - Each narration must be between 10 and 20 words
        - Visual keywords must be concrete and searchable
        Good: "ocean waves sunset", "astronaut floating space"
        Bad: "peacefulness", "the concept of gravity"
        - No markdown in your response, pure JSON only
        """
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    raw_text = response.text
    
    # Strip markdown code fences if present
    raw = raw_text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    
    # Parse JSON
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {raw_text}")
    
    # Validate structure
    if "title" not in result:
        raise ValueError("Missing 'title' key in response")
    
    if "scenes" not in result:
        raise ValueError("Missing 'scenes' key in response")
    
    scenes = result["scenes"]
    if len(scenes) != SCENE_COUNT:
        raise ValueError(f"Expected {SCENE_COUNT} scenes, got {len(scenes)}")
    
    for scene in scenes:
        if "id" not in scene:
            raise ValueError(f"Scene missing 'id' key")
        if "narration" not in scene:
            raise ValueError(f"Scene {scene.get('id')} missing 'narration' key")
        if "visual_keyword" not in scene:
            raise ValueError(f"Scene {scene.get('id')} missing 'visual_keyword' key")
    
    # Print output
    print(f"Script generated: '{result['title']}' with {len(result['scenes'])} scenes")
    for scene in scenes:
        narration_preview = scene['narration'][:40]
        print(f"  Scene {scene['id']}: {narration_preview}...")
    
    return result


if __name__ == "__main__":
    result = generate_script("how black holes form")
    print("\nFull JSON output:")
    print(json.dumps(result, indent=2))