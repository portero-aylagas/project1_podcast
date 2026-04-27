# AI Podcast Studio

AI Podcast Studio is a Gradio app that turns source material into a short two-speaker podcast.
You can provide a PDF, a URL, pasted text, or a combination of all three. The app will:

1. Extract and combine the source content.
2. Summarize the content with OpenAI.
3. Convert the summary into a two-speaker dialogue.
4. Generate MP3 audio and a transcript file.

## Project structure

```text
project1_podcast/
├── README.md
├── requirements.txt
└── src/
    ├── config.py
    ├── data_processor.py
    ├── llm_processor.py
    ├── main.py
    └── tts_generator.py
```

## Requirements

- Python 3.10+
- An OpenAI API key
- `ffmpeg` installed and available on your system `PATH`

`pydub` uses `ffmpeg` to export the final MP3. If `ffmpeg` is missing, podcast audio generation will fail even if the Python dependencies are installed correctly.

## Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run the app

```bash
python -m src.main
```

Gradio will print a local URL in the terminal. Open it in your browser to use the interface.

## How it works

### Inputs

- `PDF`: Uploaded and parsed with `pypdf`
- `URL`: Downloaded with `requests` and cleaned with `BeautifulSoup`
- `Text`: Saved as a local text file and read directly

At least one source is required.

### Processing flow

- `src/data_processor.py` loads all provided sources and combines them into a single text block.
- The combined text is summarized with the OpenAI Responses API.
- `src/llm_processor.py` converts that summary into a dialogue using the format:

```text
[Speaker1]: ...
[Speaker2]: ...
```

- `src/tts_generator.py` generates one audio file per line, then merges them into a final podcast MP3.

### Outputs

Generated files are saved under `outputs/`:

- `outputs/final_podcast.mp3`
- `outputs/transcript.txt`
- `outputs/audio_parts/` for intermediate TTS segments

## Notes

- Large PDFs or long web pages may take longer to summarize and may increase API usage.
- The current app is designed around a single style: `Two person conversation`.
- Speaker voices are mapped in `src/tts_generator.py` and can be adjusted there.

## Troubleshooting

### `ValueError: API key not loaded`

Make sure `.env` exists in the project root and contains a valid `OPENAI_API_KEY`.

### Audio generation fails

Check both of the following:

- `pydub` is installed from `requirements.txt`
- `ffmpeg` is installed and available on your system `PATH`

### No output generated from a URL

Some sites block scraping or rely heavily on JavaScript-rendered content. Try pasting the text manually if the extracted page content is incomplete.
