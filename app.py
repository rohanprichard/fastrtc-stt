import numpy as np
from fastrtc import Stream, StreamHandler, get_stt_model, audio_to_bytes, AdditionalOutputs
import gradio as gr
from elevenlabs import ElevenLabs
import time
from typing import Callable
import threading
import os
import dotenv

dotenv.load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def get_stt_text(audio_data: np.ndarray, sample_rate: int) -> str:
    """Converts audio data to text using ElevenLabs API."""
    if audio_data.size == 0:
        return ""
    try:
        audio_bytes = audio_to_bytes((sample_rate, audio_data))
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_bytes,
            model_id="scribe_v1",
            tag_audio_events=False,
            language_code="eng",
            diarize=False,
        )
        return transcription.text
    except Exception as e:
        print(f"Error during STT API call: {e}")
        return ""
    

class TranscriptionHandler(StreamHandler):
    def __init__(self, stt_fn: Callable[[np.ndarray, int], str]) -> None:
        super().__init__()
        self.stt_fn = stt_fn
        self.event = threading.Event()
        self.audio_data_buffer = np.array([], dtype=np.int16)
        self.sample_rate = None
        self.chunk_duration = 4.0
        self.overlap_duration = 0.5
        self.chunk_samples = None
        self.overlap_samples = None
        self.samples_to_remove = None

    def receive(self, frame: tuple[int, np.ndarray]) -> None:
        try:
            incoming_rate, audio_data = frame

            if self.sample_rate is None:
                self.sample_rate = incoming_rate
                self.chunk_samples = int(self.chunk_duration * self.sample_rate)
                self.overlap_samples = int(self.overlap_duration * self.sample_rate)
                self.samples_to_remove = self.chunk_samples - self.overlap_samples
                print(f"Initialized - Rate: {self.sample_rate}, Chunk samples: {self.chunk_samples}, Overlap samples: {self.overlap_samples}, Samples to remove: {self.samples_to_remove}")

            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            self.audio_data_buffer = np.concatenate((self.audio_data_buffer, audio_data))

            if self.chunk_samples is not None and len(self.audio_data_buffer) >= self.chunk_samples:
                 self.event.set()

        except Exception as e:
            print(f"Error in transcription receive: {e}")
        return None

    def emit(self) -> AdditionalOutputs | None:
        
        if not self.event.is_set():
            return None

        if self.chunk_samples is None or self.sample_rate is None or self.samples_to_remove is None:
             print("Emit called before initialization complete.")
             return None

        try:
            chunk_to_process = self.audio_data_buffer[:self.chunk_samples]
            self.audio_data_buffer = self.audio_data_buffer[self.samples_to_remove:]

            text = self.stt_fn(chunk_to_process, self.sample_rate)
            print(f"Emitted chunk: '{text}'")

            output = AdditionalOutputs(text.strip())

            if len(self.audio_data_buffer) < self.chunk_samples:
                self.event.clear()
            
            return output

        except Exception as e:
            print(f"Error in transcription emit: {e}")
            self.event.clear()
            self.audio_data_buffer = np.array([], dtype=np.int16)
            return None


    def copy(self) -> StreamHandler:
        # Pass the stt_fn when copying
        return TranscriptionHandler(stt_fn=self.stt_fn)

    def shutdown(self) -> None:
        pass

    def start_up(self) -> None:
        pass

stream = Stream(
    handler=TranscriptionHandler(stt_fn=get_stt_text),
    modality="audio",
    mode="send",
    additional_outputs=[gr.Textbox(label="Transcription", lines=5)],
    additional_outputs_handler=lambda current_val, new_val: \
        str(current_val or '') + (' ' + str(new_val) if new_val else '')
)

stream.ui.launch() 