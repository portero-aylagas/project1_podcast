"""
Convert summary text into a structured two-speaker podcast script.

The output format is intentionally strict so the downstream TTS module can parse
each line and assign a voice to each speaker.
"""

from src.config import client


def generate_podcast_script(
    summary_text: str,
    target_audience: str = "General Public",
    style: str = "Two person conversation",
) -> str:
    """Generate a podcast dialogue from summarized source material."""
    if not summary_text or not summary_text.strip():
        raise ValueError("summary_text is empty.")

    prompt = f"""
You are a podcast script writer.

Convert the following text into a podcast conversation.

Target audience: {target_audience}
Style: {style}

Rules:
- Use exactly this format:
  [Speaker1]: ...
  [Speaker2]: ...
- Alternate between Speaker1 and Speaker2.
- Keep it natural and clear.
- Adapt vocabulary and complexity to the target audience.
- Do not add narration.
- Do not add titles.
- Do not add markdown.
- Output only the dialogue as a single string.
- Separate each speaker intervention with a new line.

TEXT:
{summary_text}
"""

    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
        temperature=0.5,
    )

    return response.output_text.strip()
