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

OUTPUT_DIR = Path("outputs")
TRANSCRIPT_PATH = OUTPUT_DIR / "transcript.txt"


def reset_data():
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    URL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def pipeline(pdf_file, url_input, text_input, target_audience, style):
    reset_data()

    sources = {
        "pdf_path": None,
        "text_path": None,
        "url_path": None,
        "url": None,
        "target_audience": target_audience,
        "style": style,
    }

    if pdf_file is not None:
        pdf_destination = PDF_DIR / Path(pdf_file.name).name
        shutil.copy(pdf_file.name, pdf_destination)
        sources["pdf_path"] = str(pdf_destination)

    if text_input and text_input.strip():
        text_destination = TEXT_DIR / "input.txt"
        with open(text_destination, "w", encoding="utf-8") as f:
            f.write(text_input.strip())
        sources["text_path"] = str(text_destination)

    if url_input and url_input.strip():
        clean_url = url_input.strip()
        url_destination = URL_DIR / "url.txt"

        with open(url_destination, "w", encoding="utf-8") as f:
            f.write(clean_url)

        sources["url_path"] = str(url_destination)
        sources["url"] = clean_url

    if not any([sources["pdf_path"], sources["text_path"], sources["url"]]):
        raise gr.Error("Provide at least one source.")

    summary = dp.process_sources(sources)

    script = llm.generate_podcast_script(
        summary_text=summary,
        target_audience=target_audience,
        style=style,
    )

    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(script)

    audio_path = tts.generate_podcast_audio(script)

    return audio_path, script, str(TRANSCRIPT_PATH)


def start_processing():
    return (
        "Generating podcast...",
        gr.update(visible=False),
    )


def finish_processing(audio, transcript, transcript_file):
    return (
        "",
        gr.update(visible=True),
        audio,
        transcript,
        transcript_file,
    )


with gr.Blocks(title="AI Podcast Studio") as demo:
    gr.Markdown("# AI Podcast Studio")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Input")

            pdf_file = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
            )

            url_input = gr.Textbox(
                label="Paste URL",
                placeholder="https://...",
            )

            text_input = gr.Textbox(
                label="Paste text",
                lines=8,
            )

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

            submit_button = gr.Button(
                "Generate Podcast",
                size="lg",
                variant="primary",
            )

            status = gr.Markdown("")

        with gr.Column(scale=1):
            gr.Markdown("## Output")

            audio_output = gr.Audio(
                type="filepath",
                label="Podcast",
                interactive=False,
            )

            transcript_output = gr.Textbox(
                label="Transcript",
                lines=18,
                interactive=False,
            )

            transcript_download = gr.File(
                label="Download Transcript",
                interactive=False,
            )

    submit_button.click(
        fn=start_processing,
        inputs=[],
        outputs=[status, submit_button],
    ).then(
        fn=pipeline,
        inputs=[pdf_file, url_input, text_input, target_audience, style],
        outputs=[audio_output, transcript_output, transcript_download],
        show_progress=True,
    ).then(
        fn=finish_processing,
        inputs=[audio_output, transcript_output, transcript_download],
        outputs=[
            status,
            submit_button,
            audio_output,
            transcript_output,
            transcript_download,
        ],
    )


demo.queue()


if __name__ == "__main__":
    demo.launch()