"""
Converts summarized source content into a podcast dialogue script.

Input:
- summary text from data_processor.py
- target audience
- style

Output:
- podcast script as a single Python string
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_podcast_script(
    summary_text: str,
    target_audience: str = "General Public",
    style: str = "Two person conversation",
) -> str:
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