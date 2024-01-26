import json
import base64
import io
import tempfile
import subprocess
import os
import numpy as np
from pydub import AudioSegment, silence
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import torch
from transformers import pipeline
import asyncio

class VoiceAssistant(AsyncWebsocketConsumer):
    async def connect(self):
        self.current_sequence = io.BytesIO()
        self.current_audio_segment = AudioSegment.empty()
        self.SILENCE_THRESHOLD = -50  # Threshold in dB
        self.SILENCE_DURATION = 1000  # milliseconds
        self.silence_accumulated = 0  # Track accumulated silence duration
        await self.accept()

    async def disconnect(self, close_code):
        pass

    def detect_silences(self, audio_segment):
        dBFS = audio_segment.dBFS
        silences = silence.detect_silence(audio_segment, min_silence_len=1000, silence_thresh=dBFS-16)
        return [(start/1000, stop/1000) for start, stop in silences]

    async def receive(self, text_data):
        audio = json.loads(text_data)['audio']
        audio_chunk = base64.b64decode(audio)

        self.current_sequence.write(audio_chunk)
    
        chunk_audio_segment = AudioSegment.from_raw(io.BytesIO(audio_chunk), sample_width=2, channels=1, frame_rate=44100)
        
        # Append to the current audio
        self.current_audio_segment += chunk_audio_segment

        # Detect silences in the current audio
        silences = self.detect_silences(self.current_audio_segment)
        
        # Check accumulated silence
        last_silence_end = 0
        for start, stop in silences:
            if start - last_silence_end > 1:
                self.silence_accumulated = 0
            self.silence_accumulated += (stop - start) * 1000
            last_silence_end = stop

        if self.silence_accumulated >= self.SILENCE_DURATION:
            prediction = await self.async_process_sequence(self.current_sequence.getvalue())
            self.current_sequence = io.BytesIO()
            self.current_audio_segment = AudioSegment.empty()  # Resetting the audio segment
            self.silence_accumulated = 0

    async def async_process_sequence(self, raw_audio: bytes) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_sequence, raw_audio)

    def process_sequence(self, raw_audio: bytes) -> str:
        print("converting to wav")
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pcm") as pcm_file, \
             tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as wav_file:

            # Save raw audio
            pcm_file.write(raw_audio)
            pcm_file.flush()

            # Convert PCM to WAV
            try:
                cmd = ['ffmpeg', '-f', 's16le', '-ar', '44100', '-ac', '1', '-i', pcm_file.name, wav_file.name]
                subprocess.run(cmd, check=True)  # This will raise an error if ffmpeg fails
            except subprocess.CalledProcessError:
                return "Error during audio processing."

            # ASR prediction
            try:
                device = "cuda:0" if torch.cuda.is_available() else "cpu"
                pipe = pipeline("automatic-speech-recognition", model="openai/whisper-small", chunk_length_s=30, device=device)
                prediction = pipe(wav_file.name, batch_size=8)["text"]
            except Exception as e:
                return f"Error during transcription: {e}"

            print(prediction)
            return prediction
