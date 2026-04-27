"""
Converts a podcast script string into an audio file.

Input:
- podcast script string in this format:
  [Speaker1]: ...
  [Speaker2]: ...

Output:
- path to the final generated podcast audio file
"""

import re
import shutil
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from src.config import client


OUTPUT_DIR = Path("outputs")
PARTS_DIR = OUTPUT_DIR / "audio_parts"

VOICE_MAP = {
    "Speaker1": "alloy",
    "Speaker2": "nova",
}


def reset_audio_outputs():
    if PARTS_DIR.exists():
        shutil.rmtree(PARTS_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PARTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_script(script: str) -> list[tuple[str, str]]:
    segments = []

    for line in script.splitlines():
        match = re.match(r"\[(.*?)\]:\s*(.*)", line.strip())

        if match:
            speaker = match.group(1)
            text = match.group(2)

            if text:
                segments.append((speaker, text))

    return segments


def generate_tts(text: str, voice: str, output_path: Path) -> None:
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )

    with open(output_path, "wb") as f:
        f.write(response.content)


def build_audio_segments(segments: list[tuple[str, str]]) -> list[Path]:
    files = []

    for i, (speaker, text) in enumerate(segments):
        voice = VOICE_MAP.get(speaker, "alloy")
        filename = PARTS_DIR / f"{i:03d}_{speaker}.mp3"

        print(f"[{i + 1}/{len(segments)}] {speaker}: {text[:60]}...")

        generate_tts(
            text=text,
            voice=voice,
            output_path=filename,
        )

        files.append(filename)

    return files


def combine_audio(files: list[Path]) -> Path:
    output_file = OUTPUT_DIR / "final_podcast.mp3"

    pause = AudioSegment.silent(duration=500)
    combined = AudioSegment.empty()

    for i, file in enumerate(files):
        combined += AudioSegment.from_file(file)

        if i < len(files) - 1:
            combined += pause

    combined.export(output_file, format="mp3")

    return output_file


def generate_podcast_audio(script: str) -> str:
    """
    Main function called from main.py.

    Takes podcast script text and returns final audio file path.
    """
    if not script or not script.strip():
        raise ValueError("Podcast script is empty.")

    reset_audio_outputs()

    segments = parse_script(script)

    if not segments:
        raise ValueError(
            "Script format invalid. Expected:\n"
            "[Speaker1]: Hello\n"
            "[Speaker2]: Hi"
        )

    files = build_audio_segments(segments)
    final = combine_audio(files)

    return str(final)