"""
Convert a podcast script into audio files and a final merged MP3.

The script must contain one speaker turn per line using the format
`[SpeakerName]: text`. Each line is rendered with OpenAI TTS and then combined
into a single podcast file with short pauses between turns.
"""

import re
import shutil
from pathlib import Path

from pydub import AudioSegment

from src.config import client


OUTPUT_DIR = Path("outputs")
PARTS_DIR = OUTPUT_DIR / "audio_parts"

VOICE_MAP = {
    "Speaker1": "alloy",
    "Speaker2": "nova",
}


def reset_audio_outputs():
    """Remove old generated audio and recreate output folders."""
    if PARTS_DIR.exists():
        shutil.rmtree(PARTS_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PARTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_script(script: str) -> list[tuple[str, str]]:
    """Split the generated script into ordered `(speaker, text)` segments."""
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
    """Generate one MP3 clip for a single line of dialogue."""
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )

    with open(output_path, "wb") as f:
        f.write(response.content)


def build_audio_segments(segments: list[tuple[str, str]]) -> list[Path]:
    """Render all dialogue segments into individual MP3 files."""
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
    """Merge the generated audio files into one final podcast MP3."""
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
    """Generate the final podcast audio file from a validated script."""
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
