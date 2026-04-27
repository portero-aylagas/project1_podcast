import shutil
from pathlib import Path
import gradio as gr

# placeholders for later integration
import src.data_processor as dp
import src.llm_processor as llm
import src.tts_generator as tts


SOURCE_DIR = Path("source")
PDF_DIR = SOURCE_DIR / "pdf"
TEXT_DIR = SOURCE_DIR / "text"
URL_DIR = SOURCE_DIR / "url"

PDF_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DIR.mkdir(parents=True, exist_ok=True)
URL_DIR.mkdir(parents=True, exist_ok=True)


def save_sources(pdf_file, url_input, text_input):
    locations = {}

    if pdf_file is not None:
        pdf_destination = PDF_DIR / Path(pdf_file.name).name
        shutil.copy(pdf_file.name, pdf_destination)
        locations["pdf_path"] = str(pdf_destination)

    if url_input and url_input.strip():
        url_destination = URL_DIR / "url.txt"
        with open(url_destination, "w", encoding="utf-8") as f:
            f.write(url_input.strip())
        locations["url_path"] = str(url_destination)
        locations["url"] = url_input.strip()

    if text_input and text_input.strip():
        text_destination = TEXT_DIR / "input.txt"
        with open(text_destination, "w", encoding="utf-8") as f:
            f.write(text_input.strip())
        locations["text_path"] = str(text_destination)

    if not locations:
        raise gr.Error("Provide at least one source: PDF, URL, or text.")

    return locations


with gr.Blocks(title="Source Loader") as demo:
    gr.Markdown("# Source Loader")

    pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
    url_input = gr.Textbox(label="Paste URL", placeholder="https://...")
    text_input = gr.Textbox(label="Paste text", lines=8)

    submit_button = gr.Button("Submit sources")

    output = gr.JSON(label="Saved source locations")

    submit_button.click(
        fn=save_sources,
        inputs=[pdf_file, url_input, text_input],
        outputs=output,
    )


if __name__ == "__main__":
    demo.launch()