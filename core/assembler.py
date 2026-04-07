# core/assembler.py
import ffmpeg
import os
from pydub import AudioSegment
from config import (
    CLIPS_DIR,
    AUDIO_DIR,
    OUTPUT_DIR,
    FINAL_VIDEO,
    SUBTITLE_FILE,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS
)


def get_audio_duration(audio_path: str) -> float:
    """
    Measures and returns exact audio duration in seconds as a float using pydub.
    """
    audio = AudioSegment.from_mp3(audio_path)
    return len(audio) / 1000.0


def merge_scene(clip_path: str, audio_path: str, output_path: str, duration: float) -> str:
    """
    Takes one video clip and one audio file and produces a single merged MP4 where:
    - Video is trimmed or looped to exact duration
    - Audio is attached to that video
    - Output is saved to output_path
    """
    # Step 1 — determine if clip needs trim or loop
    probe = ffmpeg.probe(clip_path)
    video_stream = next(
        s for s in probe['streams']
        if s['codec_type'] == 'video'
    )
    clip_duration = float(video_stream.get('duration', 0))

    # Step 2 — build video input accordingly
    if clip_duration >= duration:
        video_input = ffmpeg.input(clip_path, t=duration)
    else:
        video_input = ffmpeg.input(clip_path, stream_loop=-1, t=duration)

    # Step 3 — build audio input
    audio_input = ffmpeg.input(audio_path)

    # Step 4 — combine and output
    ffmpeg.output(
        video_input,
        audio_input,
        output_path,
        vcodec='libx264',
        acodec='aac',
        t=duration,
        shortest=None
    ).run(overwrite_output=True, quiet=True)

    return output_path


def concatenate_scenes(merged_paths: list, output_path: str) -> str:
    """
    Takes a list of merged per-scene MP4 file paths, concatenates them in order into one combined MP4 using the FFmpeg concat demuxer via a filelist.txt file.
    """
    # Step 1 — write filelist.txt
    filelist_path = f"{OUTPUT_DIR}/filelist.txt"
    with open(filelist_path, "w") as f:
        for path in merged_paths:
            abs_path = os.path.abspath(path)
            f.write(f"file '{abs_path}'\n")

    # Step 2 — run concat
    ffmpeg.input(
        filelist_path,
        format='concat',
        safe=0
    ).output(
        output_path,
        c='copy'
    ).run(overwrite_output=True, quiet=True)

    # Step 3 — delete filelist.txt after use
    os.remove(filelist_path)

    return output_path


def burn_subtitles(input_path: str, subtitle_path: str, output_path: str) -> str:
    """
    Takes the combined video and burns the SRT subtitle file directly into the video frames (hardcoded subtitles — not soft subs).
    """
    safe_subtitle = subtitle_path.replace('\\', '/').replace(':', '\\:')

    style = (
        'FontSize=20,'
        'PrimaryColour=&Hffffff,'
        'OutlineColour=&H000000,'
        'Outline=2,'
        'BorderStyle=1,'
        'Alignment=2'
    )

    input_video = ffmpeg.input(input_path)
    video = input_video.filter('subtitles', safe_subtitle, force_style=style)
    audio = input_video.audio

    (
        ffmpeg
        .output(video, audio, output_path, vcodec='libx264', acodec='aac')
        .run(overwrite_output=True, quiet=True)
    )

    return output_path


def assemble(scene_data: list, subtitle_path: str) -> str:
    """
    Orchestrates all assembly steps in sequence. This is the only function called by main.py.
    """
    print(f"Starting assembly of {len(scene_data)} scenes...")

    merged_paths = []

    # STEP 1 — per scene merge
    for item in scene_data:
        duration = get_audio_duration(item['audio_path'])
        merged_path = f"{CLIPS_DIR}/scene_{item['scene_id']}_merged.mp4"
        merge_scene(item['clip_path'], item['audio_path'], merged_path, duration)
        merged_paths.append(merged_path)
        print(f"  [Step 1 - {item['scene_id']}/{len(scene_data)}] Merging scene (duration: {duration:.2f}s)...")

    # STEP 2 — concatenate all merged scenes
    print(f"  [Step 2] Concatenating {len(merged_paths)} scenes...")
    combined_path = f"{OUTPUT_DIR}/combined.mp4"
    concatenate_scenes(merged_paths, combined_path)

    # STEP 3 — burn subtitles
    print(f"  [Step 3] Burning subtitles...")
    burn_subtitles(combined_path, subtitle_path, FINAL_VIDEO)

    # STEP 4 — cleanup intermediate files
    print(f"  [Step 4] Cleaning up intermediate files...")
    for path in merged_paths:
        if os.path.exists(path):
            os.remove(path)
    if os.path.exists(combined_path):
        os.remove(combined_path)

    # STEP 5 — return FINAL_VIDEO path
    print(f"Assembly complete! Final video: {FINAL_VIDEO}")
    return FINAL_VIDEO


if __name__ == "__main__":
    test_scene_data = [
        {
            "scene_id": 1,
            "clip_path": "output/clips/scene_1.mp4",
            "audio_path": "output/audio/scene_1.mp3"
        },
        {
            "scene_id": 2,
            "clip_path": "output/clips/scene_2.mp4",
            "audio_path": "output/audio/scene_2.mp3"
        },
        {
            "scene_id": 3,
            "clip_path": "output/clips/scene_3.mp4",
            "audio_path": "output/audio/scene_3.mp3"
        },
        {
            "scene_id": 4,
            "clip_path": "output/clips/scene_4.mp4",
            "audio_path": "output/audio/scene_4.mp3"
        },
        {
            "scene_id": 5,
            "clip_path": "output/clips/scene_5.mp4",
            "audio_path": "output/audio/scene_5.mp3"
        }
    ]

    final = assemble(test_scene_data, "output/subtitles.srt")

    print("\nResult summary:")
    exists = os.path.exists(final)
    size = os.path.getsize(final) if exists else 0
    size_mb = round(size / 1024 / 1024, 2)
    print(f"  final.mp4 exists: {exists}")
    print(f"  final.mp4 size:   {size_mb} MB")
