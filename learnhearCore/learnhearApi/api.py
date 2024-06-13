from ninja.security import HttpBasicAuth
from ninja import Router
from TTS.api import TTS
from transformers import pipeline
import asyncio
from faster_whisper import WhisperModel
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from IPython.display import Audio
import time 
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from lessons.models import Lesson, LyricsTimestamp
from practices.models import *
from django.db import IntegrityError, transaction
from datetime import timedelta
from io import BytesIO
from ninja.files import UploadedFile
from ninja import NinjaAPI, File
from django.core.files import File as djangoFile
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from django.http import StreamingHttpResponse
import boto3
import os
from django.conf import settings

router = Router()

class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        if username == "admin" and password == "secret":
            return username
          


@router.post('/sythesize/')
def synthesize(request, text: str = (...)):
    polly_client = boto3.Session(
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,                     
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.REGION_NAME).client('polly')
    
    response = polly_client.synthesize_speech(VoiceId='Joanna',
                OutputFormat='mp3', 
                Text = 'This is a sample text to be synthesized.',
                Engine = 'neural')

    # Get the audio stream
    audio_bytes = response['AudioStream'].read()

    # Return the raw audio bytes as a streaming response
    response = StreamingHttpResponse(
        streaming_content=(chunk for chunk in iter(lambda: audio_bytes, b""))
    )
    response['Content-Type'] = 'audio/mpeg'
    return response
    



def chunk_text(text, max_chars):
    """
    Chunks the text based on sentences using nltk and a character limit.
    """
    sentences = sent_tokenize(text)
    
    current_chunk = ""
    chunks = []
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chars:
            # Current chunk will exceed the limit if we add this sentence.
            # Save current chunk and start a new one.
            chunks.append(current_chunk.strip())
            current_chunk = ""

        current_chunk += " " + sentence

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


@router.post('/upload/')
def save_lesson_and_timestamp(request,filepath: UploadedFile = File(...),title: str = (...),word: str = (...),category: str = (...),correct_answer: str = (...),choice: str = (...)):
    
    try:
        
        with transaction.atomic():
            file_content = filepath.read()

            # Create a ContentFile from the file content
            content_file = ContentFile(file_content)

            practice, created = Practice.objects.get_or_create(
                title=title,
                category=category,
                practice_audio=filepath,
                choices=choice,
                correct_answer=correct_answer
            )
            
                        
            model = WhisperModel("small.en", device="cpu", compute_type="int8")
            segments, info = model.transcribe(content_file, word_timestamps=True)
            
            lyrics_data = []
            
            for segment in segments:
                for word in segment.words:

                    word_end_seconds = word.end

                    # Calculate hours, minutes, and seconds
                    hours, remainder = divmod(word_end_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    # Format the result as a string in the "00:00:00" format
                    formatted_time = "%02d:%02d:%02d" % (hours, minutes, seconds)
                    print(formatted_time)
                    

                    try:
                    # Try to create a new LyricsTimestamp
                        timestamp, created = PracticeTimestamp.objects.get_or_create(
                            practice=practice,
                            timestamp=formatted_time,
                            lyrics=word.word
                        )
                        
                        lyrics_data.append({"timestamp":formatted_time,"lyrics":word.word})
                    except IntegrityError:
                            # If IntegrityError is raised, it means the entry already exists, so update it
                            timestamp = PracticeTimestamp.objects.get(practice=practice, timestamp=formatted_time)
                            timestamp.lyrics = word.word
                            timestamp.save()
                            
            
            return lyrics_data      
    except IntegrityError as e:
        print(e) 
        
async def generate_tts_audio(text, speaker_wav, language, emotion, speed, filepath):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    tts.tts_to_file(text=text,
                   file_path=filepath,
                   speaker_wav=speaker_wav,
                   language=language,
                   emotion=emotion,
                   speed=speed)
    
    return filepath
            
