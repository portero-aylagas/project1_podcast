from config import client
from pydub import AudioSegment
from pydub.playback import play
import io

voices = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]
text = "The quick brown fox jumps over the lazy dog. How does my voice sound?"

for voice in voices:
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text
    )
    
    print(f"Playing: {voice}")
    
    # Play audio directly
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    play(audio)
    
    print(f"Finished: {voice}")