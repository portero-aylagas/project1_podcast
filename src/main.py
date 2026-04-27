import shutil
from pathlib import Path
import gradio as gr

import src.data_processor as dp
import src.llm_processor as llm
import src.tts_generator as tts


DATA_DIR = Path("data")
PDF_DIR = DATA_DIR / "pdf"
TEXT_DIR = DATA_DIR / "text"
URL_DIR = DATA_DIR / "url"


def reset_data():
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    URL_DIR.mkdir(parents=True, exist_ok=True)


latest_sources = {
    "pdf_path": None,
    "text_path": None,
    "url_path": None,
    "url": None,
    "target_audience": None,
    "style": None,
}

latest_summary = None
latest_podcast_script = None
latest_audio_path = None


def save_sources(pdf_file, url_input, text_input, target_audience, style):
    global latest_summary, latest_podcast_script, latest_audio_path

    reset_data()

    latest_sources["pdf_path"] = None
    latest_sources["text_path"] = None
    latest_sources["url_path"] = None
    latest_sources["url"] = None
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
        clean_url = url_input.strip()

        url_destination = URL_DIR / "url.txt"
        with open(url_destination, "w", encoding="utf-8") as f:
            f.write(clean_url)

        latest_sources["url_path"] = str(url_destination)
        latest_sources["url"] = clean_url

    if not any([
        latest_sources["pdf_path"],
        latest_sources["text_path"],
        latest_sources["url"],
    ]):
        raise gr.Error("Provide at least one source.")

    latest_summary = dp.process_sources(latest_sources)

    latest_podcast_script = llm.generate_podcast_script(
        summary_text=latest_summary,
        target_audience=target_audience,
        style=style,
    )

    latest_audio_path = tts.generate_podcast_audio(latest_podcast_script)

    print(f"Saved sources: {latest_sources}")
    print(f"latest_summary: {latest_summary}")
    print(f"latest_podcast_script: {latest_podcast_script}")
    print(f"latest_audio_path: {latest_audio_path}")

    return latest_audio_path, latest_podcast_script


with gr.Blocks(title="AI Podcast Studio") as demo:
    gr.Markdown("# AI Podcast Studio")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Input")

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

            submit_button = gr.Button("Generate Podcast")

        with gr.Column(scale=1):
            gr.Markdown("## Output")

            audio_output = gr.Audio(
                label="Generated Podcast",
                type="filepath",
            )

            transcript_output = gr.Textbox(
                label="Transcript",
                lines=18,
                interactive=False,
            )

    submit_button.click(
        fn=save_sources,
        inputs=[pdf_file, url_input, text_input, target_audience, style],
        outputs=[audio_output, transcript_output],
    )


if __name__ == "__main__":
    demo.launch()