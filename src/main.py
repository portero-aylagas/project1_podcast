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


def reset_sources():
    if SOURCE_DIR.exists():
        shutil.rmtree(SOURCE_DIR)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    URL_DIR.mkdir(parents=True, exist_ok=True)


latest_sources = {
    "pdf_path": None,
    "text_path": None,
    "url_path": None,
    "target_audience": None,
    "style": None,
}


def save_sources(pdf_file, url_input, text_input, target_audience, style):
    # clean previous run
    reset_sources()

    # reset tracking
    latest_sources["pdf_path"] = None
    latest_sources["text_path"] = None
    latest_sources["url_path"] = None
    latest_sources["target_audience"] = target_audience
    latest_sources["style"] = style

    if pdf_file is not None:
        pdf_destination = PDF_DIR / Path(pdf_file.name).name
        shutil.copy(pdf_file.name, pdf_destination)
        latest_sources["pdf_path"] = str(pdf_destination)

    if text_input and text_input.strip():
        text_destination = TEXT_DIR / "input.txt"
        with open(text_destination, "w", encoding="utf-8") as f:
            f.write(text_input.strip())
        latest_sources["text_path"] = str(text_destination)

    if url_input and url_input.strip():
        url_destination = URL_DIR / "url.txt"
        with open(url_destination, "w", encoding="utf-8") as f:
            f.write(url_input.strip())
        latest_sources["url_path"] = str(url_destination)

    if not any([
        latest_sources["pdf_path"],
        latest_sources["text_path"],
        latest_sources["url_path"]
    ]):
        raise gr.Error("Provide at least one source.")

    print("Saved sources:", latest_sources)

    return "Sources saved."


with gr.Blocks(title="Source Loader") as demo:
    pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
    url_input = gr.Textbox(label="Paste URL")
    text_input = gr.Textbox(label="Paste text", lines=8)

    target_audience = gr.Dropdown(
        choices=["Kids", "General Public", "Professionals", "Experts"],
        value="General Public",
        label="Target Audience",
    )

    style = gr.Dropdown(
        choices=["Two person conversation"],
        value="Two person conversation",
        label="Style",
    )

    submit_button = gr.Button("Submit sources")
    hidden_status = gr.Textbox(visible=False)

    submit_button.click(
        fn=save_sources,
        inputs=[pdf_file, url_input, text_input, target_audience, style],
        outputs=hidden_status,
    )


if __name__ == "__main__":
    demo.launch()