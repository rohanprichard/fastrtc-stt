# FastRTC Speech-to-Text Demos

Two small FastRTC + Gradio experiments for working with live audio in Python:

1. `app.py` transcribes microphone audio using ElevenLabs.
2. `save_audio_app.py` receives live audio and writes chunked WAV files.

## Requirements

- Python 3
- an ElevenLabs API key for the transcription demo
- a browser that supports microphone input

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file for the transcription demo:

```env
ELEVENLABS_API_KEY=your_key_here
```

Keep this file out of source control.

## Run

```bash
python app.py
```

Gradio prints a local URL. Open it, grant microphone access, and speak to see the live transcription. Run `python save_audio_app.py` to use the audio-saving experiment instead.

## Notes

The transcription path sends audio to ElevenLabs and therefore requires your own API key and account. The audio-saving path writes files locally; review generated files before sharing them.

## License

MIT
