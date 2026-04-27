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
    sections = []

    if source_info.get("text_path"):
        sections.append(
            "--- SOURCE: TEXT ---\n"
            f"{load_txt(source_info['text_path']).strip()}"
        )

    if source_info.get("pdf_path"):
        sections.append(
            "--- SOURCE: PDF ---\n"
            f"{load_pdf(source_info['pdf_path']).strip()}"
        )

    if source_info.get("url"):
        sections.append(
            "--- SOURCE: URL ---\n"
            f"{load_url(source_info['url']).strip()}"
        )

    return "\n\n".join(section for section in sections if section.strip())


def summarize_text(text: str, target_audience: str) -> str:
    """Summarize the combined source material with the OpenAI Responses API."""
    prompt = f"""
You are preparing source material for a two-person podcast conversation.

You will receive multiple sources. Every source must be used.
Do not ignore information just because one source is shorter, longer, more detailed,
or more general than the others.

Your task:
1. Read all sources carefully.
2. Identify the key points, examples, incidents, and claims from each source.
3. Produce one integrated summary that reflects all sources fairly.
4. Preserve concrete examples and unique details, even if they appear in only one source.
5. If sources overlap, merge them cleanly.
6. If sources differ, include the distinct perspectives or examples instead of dropping them.
7. Before finishing, check that every source contributed at least one meaningful detail to the final summary.

Output requirements:
- Write a clear, concise summary.
- Tailor the tone and complexity to the target audience.
- Make the summary suitable for conversion into a two-person podcast conversation.
- Do not mention source labels like "TEXT", "PDF", or "URL" in the final summary.

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
