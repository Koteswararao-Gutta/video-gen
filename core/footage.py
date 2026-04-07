# core/footage.py

import requests
import os
from config import (
    PEXELS_API_KEY,
    PEXELS_PER_PAGE,
    CLIPS_DIR
)


def search_footage(keyword: str) -> str:
    """Search Pexels videos for the keyword and return the best video file URL."""
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keyword,
        "per_page": PEXELS_PER_PAGE,
        "orientation": "portrait"
    }
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    data = response.json()

    videos = data.get("videos", [])
    if not videos:
        raise ValueError(f"No footage found on Pexels for keyword: '{keyword}'")

    first_video = videos[0]
    video_files = first_video.get("video_files", [])

    selected_file = None
    for file in video_files:
        if file.get("quality") == "hd" and file.get("width", 0) >= 1280:
            selected_file = file
            break

    if selected_file is None:
        for file in video_files:
            if file.get("quality") == "sd" and file.get("width", 0) >= 1280:
                selected_file = file
                break

    if selected_file is None and video_files:
        selected_file = video_files[0]

    if selected_file is None:
        raise ValueError(f"No video file available for keyword: '{keyword}'")

    return selected_file.get("link")


def download_footage(url: str, output_path: str) -> str:
    """Download a video file from the URL to the specified output path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    return output_path


def get_footage(keyword: str, output_path: str) -> str:
    """Search and download a single footage clip for the provided keyword."""
    url = search_footage(keyword)
    return download_footage(url, output_path)


def get_footage_for_scenes(scenes: list) -> list:
    """Download footage clips for each scene and return metadata for the generated clips."""
    print(f"Fetching footage for {len(scenes)} scenes...")
    results = []
    total = len(scenes)

    for scene in scenes:
        print(f"  [{scene['id']}/{total}] Searching: '{scene['visual_keyword']}'")
        url = search_footage(scene["visual_keyword"])
        output_path = f"{CLIPS_DIR}/scene_{scene['id']}.mp4"
        download_footage(url, output_path)
        print(f"  [{scene['id']}/{total}] Downloaded: scene_{scene['id']}.mp4")
        results.append({
            "scene_id": scene["id"],
            "clip_path": output_path,
            "visual_keyword": scene["visual_keyword"]
        })

    print(f"Footage complete. Files saved to: {CLIPS_DIR}/")
    return results


if __name__ == "__main__":
    os.makedirs("output/clips", exist_ok=True)

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

    footage_data = get_footage_for_scenes(test_scenes)

    print("\nResult summary:")
    for item in footage_data:
        exists = os.path.exists(item["clip_path"])
        size = os.path.getsize(item["clip_path"]) if exists else 0
        size_mb = round(size / 1024 / 1024, 2)
        print(f"  scene_{item['scene_id']}.mp4 — exists: {exists}, size: {size_mb} MB")
