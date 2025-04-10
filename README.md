# FastRTC STT and Audio Saving Demo

This project demonstrates real-time audio processing using the `fastrtc` library with Gradio interfaces. It includes two separate applications:

1.  **Real-time Speech-to-Text (STT):** Transcribes audio input in real-time using the ElevenLabs API (`app.py`).
2.  **Real-time Audio Saving:** Saves incoming audio streams into chunked `.wav` files (`save_audio_app.py`).

## Requirements

*   Python 3.x
*   Dependencies listed in `requirements.txt`:
    *   `numpy`
    *   `fastrtc[stt]`
    *   `elevenlabs`
    *   `python-dotenv`
    *   `gradio`
*   An ElevenLabs API key (for the STT app).

## Setup

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a file named `.env` in the project root directory. Add your ElevenLabs API key to this file:
    ```env
    ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY"
    ```
    Replace `"YOUR_ELEVENLABS_API_KEY"` with your actual key.

## Running the Application

### Real-time STT App

This app captures audio from your microphone and transcribes it in real-time.

```bash
python app.py
```

Navigate to the URL provided by Gradio (usually `http://127.0.0.1:7860`) in your web browser.

Navigate to the URL provided by Gradio in your web browser. Audio chunks will be saved automatically to the `saved_audio/` folder in the project directory as they are processed.
