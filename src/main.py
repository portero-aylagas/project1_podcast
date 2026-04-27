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


def log_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def reset_data():
    log_section("🧹 STEP 1 — RESET ENVIRONMENT")

    if DATA_DIR.exists():
        print(f"Deleting old data folder: {DATA_DIR}")
        shutil.rmtree(DATA_DIR)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    URL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Data folders recreated.")


def pipeline(pdf_file, url_input, text_input, target_audience, style):
    log_section("📥 INPUT RECEIVED")

    print(f"PDF provided: {pdf_file is not None}")
    print(f"URL provided: {bool(url_input and url_input.strip())}")
    print(f"Text provided: {bool(text_input and text_input.strip())}")
    print(f"Target audience: {target_audience}")
    print(f"Style: {style}")

    reset_data()

    sources = {
        "pdf_path": None,
        "text_path": None,
        "url_path": None,
        "url": None,
        "target_audience": target_audience,
        "style": style,
    }

    log_section("💾 STEP 2 — SAVE SOURCES")

    if pdf_file is not None:
        pdf_destination = PDF_DIR / Path(pdf_file.name).name
        shutil.copy(pdf_file.name, pdf_destination)
        sources["pdf_path"] = str(pdf_destination)
        print(f"PDF saved → {pdf_destination}")

    if text_input and text_input.strip():
        text_destination = TEXT_DIR / "input.txt"
        with open(text_destination, "w", encoding="utf-8") as f:
            f.write(text_input.strip())
        sources["text_path"] = str(text_destination)
        print(f"Text saved → {text_destination}")

    if url_input and url_input.strip():
        clean_url = url_input.strip()
        url_destination = URL_DIR / "url.txt"

        with open(url_destination, "w", encoding="utf-8") as f:
            f.write(clean_url)

        sources["url_path"] = str(url_destination)
        sources["url"] = clean_url
        print(f"URL saved → {url_destination}")
        print(f"URL value → {clean_url}")

    if not any([sources["pdf_path"], sources["text_path"], sources["url"]]):
        raise gr.Error("Provide at least one source.")

    print(f"Sources dictionary → {sources}")

    log_section("🔍 STEP 3 — PROCESS SOURCES")
    summary = dp.process_sources(sources)
    print(f"Summary generated ({len(summary)} characters).")
    print("\nSummary preview:")
    print(summary[:800])

    log_section("📝 STEP 4 — GENERATE PODCAST SCRIPT")
    script = llm.generate_podcast_script(
        summary_text=summary,
        target_audience=target_audience,
        style=style,
    )

    segment_count = script.count("[Speaker1]:") + script.count("[Speaker2]:")
    print(f"Podcast script generated ({len(script)} characters, {segment_count} segments).")
    print("\nScript preview:")
    print(script[:800])

    log_section("💿 STEP 5 — SAVE TRANSCRIPT")
    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"Transcript saved → {TRANSCRIPT_PATH}")

    log_section("🎙️ STEP 6 — GENERATE AUDIO")
    audio_path = tts.generate_podcast_audio(script)
    print(f"Audio generated → {audio_path}")

    log_section("📦 DONE")
    print(f"Audio file: {audio_path}")
    print(f"Transcript file: {TRANSCRIPT_PATH}")

    return audio_path, script, str(TRANSCRIPT_PATH)


def start_processing():
    return (
        "⏳ Generating podcast...",
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
                "🎙️ Generate Podcast",
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