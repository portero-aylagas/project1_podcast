"""
Loads user-provided sources and converts them into text.

Supported sources:
- Text file
- PDF file
- URL

Returns summarized text for main.py.
"""

from pathlib import Path
import os

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_url(url: str) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text(separator="\n")


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        text_parts.append(page.extract_text() or "")

    return "\n".join(text_parts)


def combine_sources(source_info: dict) -> str:
    combined_text = ""

    if source_info.get("text_path"):
        combined_text += load_txt(source_info["text_path"])
        combined_text += "\n\n---NEW SOURCE: TEXT---\n\n"

    if source_info.get("pdf_path"):
        combined_text += load_pdf(source_info["pdf_path"])
        combined_text += "\n\n---NEW SOURCE: PDF---\n\n"

    if source_info.get("url"):
        combined_text += load_url(source_info["url"])
        combined_text += "\n\n---NEW SOURCE: URL---\n\n"

    return combined_text.strip()


def summarize_text(text: str, target_audience: str, style: str) -> str:
    prompt = f"""
Summarize the following source material clearly by combining all the provided content.
The summary should be concise, engaging, and tailored to the specified target audience.

Target audience: {target_audience}

Source material:
{text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text


def process_sources(source_info: dict) -> str:
    combined_text = combine_sources(source_info)

    if not combined_text:
        raise ValueError("No source content found.")

    summary = summarize_text(
        text=combined_text,
        target_audience=source_info.get("target_audience", "General Public"),
        style=source_info.get("style", "Two person conversation"),
    )

    return summary