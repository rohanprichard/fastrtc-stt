import numpy as np
from fastrtc import Stream, StreamHandler, audio_to_bytes
import gradio as gr
import time
import wave
import os

# Removed ElevenLabs related code

class AudioSaverHandler(StreamHandler):
    def __init__(self) -> None:
        super().__init__()
        self.audio_data_buffer = np.array([], dtype=np.int16)
        # Initialize rate and chunk samples later, based on first frame
        self.sample_rate = None
        self.chunk_duration = 4.0
        self.chunk_samples = None
        # Overlap settings
        self.overlap_duration = 1.0
        self.overlap_samples = None
        self.samples_to_remove = None
        self.file_counter = 0
        self.output_dir = "saved_audio"

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_chunk_to_wav(self, audio_chunk: np.ndarray) -> None:
        """Saves an audio chunk to a WAV file."""
        if self.sample_rate is None:
            print("Error: Sample rate not yet determined.")
            return

        self.file_counter += 1
        filename = os.path.join(self.output_dir, f"chunk_{self.file_counter:04d}.wav")
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_chunk.tobytes())
            print(f"Saved audio chunk to {filename} (Rate: {self.sample_rate})")
        except Exception as e:
            print(f"Error saving audio chunk {filename}: {e}")

    def receive(self, frame: tuple[int, np.ndarray]) -> None:
        try:
            incoming_rate, audio_data = frame
            # print(f"Received frame - Rate: {incoming_rate}, Shape: {audio_data.shape}, Dtype: {audio_data.dtype}") # Diagnostic print

            # Set sample rate, chunk samples, and overlap calculations on first received frame
            if self.sample_rate is None:
                self.sample_rate = incoming_rate
                self.chunk_samples = int(self.chunk_duration * self.sample_rate)
                self.overlap_samples = int(self.overlap_duration * self.sample_rate)
                self.samples_to_remove = self.chunk_samples - self.overlap_samples
                print(f"Detected rate: {self.sample_rate}, Chunk samples: {self.chunk_samples}, Overlap samples: {self.overlap_samples}, Samples to remove: {self.samples_to_remove}")
            elif incoming_rate != self.sample_rate:
                 # Optional: Handle potential sample rate changes mid-stream if necessary
                 print(f"Warning: Sample rate changed mid-stream from {self.sample_rate} to {incoming_rate}. Sticking with the initial rate.")
                 # Or adjust logic here if dynamic rate changes need full handling

            # Ensure audio_data is 1D before concatenation
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            self.audio_data_buffer = np.concatenate((self.audio_data_buffer, audio_data))

            # Check if initialization is complete before proceeding
            if self.chunk_samples is None or self.samples_to_remove is None:
                 return # Wait until sample rate and calculations are known

            # Process chunks with overlap
            while len(self.audio_data_buffer) >= self.chunk_samples:
                chunk_to_process = self.audio_data_buffer[:self.chunk_samples]
                # Remove only the non-overlapping part from the buffer
                self.audio_data_buffer = self.audio_data_buffer[self.samples_to_remove:]

                # Save the chunk
                self.save_chunk_to_wav(chunk_to_process)

                # Removed transcription logic and send_message_sync

        except Exception as e:
            # Changed error message context
            print(f"Error in audio processing/saving: {e}")

    def emit(self) -> None:
        return None

    def copy(self) -> StreamHandler:
        # Return instance of the modified handler
        return AudioSaverHandler()

    def shutdown(self) -> None:
        pass

    def start_up(self) -> None:
        pass

stream = Stream(
    # Use the new handler
    handler=AudioSaverHandler(),
    modality="audio",
    mode="send",
    # Removed additional_outputs and additional_outputs_handler
)

stream.ui.launch() 