from src.config import client
from pydub import AudioSegment
from pydub.playback import play
import io


def generate_audio(text: str, voice: str = "nova", model: str = "tts-1-hd") -> AudioSegment:
    """
    Generates audio from text using OpenAI TTS and returns it as an AudioSegment.
    """
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )

    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    return audio


def play_audio(audio: AudioSegment) -> None:
    """
    Plays an AudioSegment locally.
    """
    play(audio)


def test_voices(text: str) -> None:
    """
    Tests all available voices using the same input text.
    """
    voices = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]

    for voice in voices:
        print(f"Playing: {voice}")
        audio = generate_audio(text=text, voice=voice)
        play_audio(audio)
        print(f"Finished: {voice}")


if __name__ == "__main__":
    sample_text = "The quick brown fox jumps over the lazy dog. How does my voice sound?"
    test_voices(sample_text)