"""
Load source material and summarize it for podcast generation.

This module accepts the sources collected by the Gradio app, extracts text from
each source type, combines everything into a single promptable document, and
returns a summary that can be converted into a podcast script.
"""

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from src.config import client


def load_txt(file_path: str) -> str:
    """Read a UTF-8 text file from disk and return its contents."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_url(url: str) -> str:
    """Fetch a web page and return visible text content only."""
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text(separator="\n")


def load_pdf(file_path: str) -> str:
    """Extract text from every page of a PDF file."""
    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        text_parts.append(page.extract_text() or "")

    return "\n".join(text_parts)


def combine_sources(source_info: dict) -> str:
    """Merge all provided source types into a single text block."""
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


def summarize_text(text: str, target_audience: str) -> str:
    """Summarize the combined source material with the OpenAI Responses API."""
    prompt = f"""
Summarize the following source material clearly by combining all the provided content.
The summary should be concise, engaging, and tailored to the specified target audience.
The output will later be turned into a two-person podcast conversation.

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
    """End-to-end source loading and summarization entry point for the app."""
    combined_text = combine_sources(source_info)

    if not combined_text:
        raise ValueError("No source content found.")

    summary = summarize_text(
        text=combined_text,
        target_audience=source_info.get("target_audience", "General Public"),
    )

    return summary
