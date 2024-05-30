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

router = Router()

class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        if username == "admin" and password == "secret":
            return username
          


@router.post('/sythesize/')
def synthesize(request, text: str = (...)):
    polly_client = boto3.Session(
                    aws_access_key_id="",                     
        aws_secret_access_key="",
        region_name='us-east-1').client('polly')
    
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
            
            # choices_objects = [PracticeQuestionChoice(practice=practice, choices=choice) for choice in choices]
            # PracticeQuestionChoice.objects.bulk_create(choices_objects)

                        
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
            
@router.get('/')
async def list_events(request):

    # generate speech by cloning a voice using default settings
    
    long_string = """
What are nouns?

Nouns are words that name people, places, animals, or things. They are like the building blocks of a sentence. Without nouns, we would not be able to say anything about the world around us.

Examples of nouns:

People: John, Mary, teacher, doctor, firefighter
Places: City, country, park, zoo, school
Animals: Dog, cat, fish, bird, snake
Things: Car, tree, book, pencil, toy
How are nouns used in a sentence?

Nouns can be used in a variety of ways in a sentence. They can be the subject, object, or complement of a verb. For example:

Subject: The dog barked loudly.
Object: I saw a cat on the roof.
Complement: The tree is very tall.
Here are some other examples of how nouns are used in a sentence:

The boy is playing with his toy.
The girl is eating an apple.
The bird is singing in the tree.
The car is driving down the street.
The house has a biggarden.
    """
    

    filepath = await generate_tts_audio(long_string, "C:/Users/NITRO 5/Desktop/wavfiles/speaker/Ayeen_Pineda.mp3", "en", "Happy", 0.5, "C:/Users/NITRO 5/Desktop/wavfiles/lesson-noun-l1.wav")
    
    
    await save_lesson_and_timestamp(filepath,"noun-1","grammar")

    return [
        "hello",
        
    ]
    # generate speech by cloning a voice using custom settings
    # tts.tts_to_file(text="It took me quite a long time to develop a voice, and now that I have it I'm not going to be silent.",
    #                 file_path="output.wav",
    #                 speaker_wav="/path/to/target/speaker.wav",
    #                 language="en",
    #                 decoder_iterations=30)
# def list_events(request):
#      # Possibly needed if there's a rate limit on calls to Suno Bark

#     preload_models(
#     text_use_small=True,
#     coarse_use_small=True,
#     fine_use_gpu=False,
#     fine_use_small=True,
# )
#     # Step 1: Text Segmentation
#     long_string = """
#  Noun is part of speech that comprise words that are used to name person, places, animals and things. What are nouns used for? They are used for naming a person, places, animals and things.
# """

    # sentences = nltk.sent_tokenize(long_string)

    # # Set up sample rate
    # SAMPLE_RATE = 22050
    # HISTORY_PROMPT = "v2/en_speaker_9"

    # chunks = ['']
    # token_counter = 0

    # for sentence in sentences:
    #     current_tokens = len(nltk.Text(sentence))
    #     if token_counter + current_tokens <= 250:
    #         token_counter = token_counter + current_tokens
    #         chunks[-1] = chunks[-1] + " " + sentence
    #     else:
    #         chunks.append(sentence)
    #         token_counter = current_tokens

    # # Generate audio for each prompt
    # audio_arrays = []
    # for prompt in chunks:
    #     audio_array = generate_audio(prompt,history_prompt=HISTORY_PROMPT)
    #     audio_arrays.append(audio_array)

    # # Combine the audio files
    # combined_audio = np.concatenate(audio_arrays)

    # write_wav("C:/Users/NITRO 5/Desktop/wavfiles/lesson-Grammar-noun-l1.wav", SAMPLE_RATE, combined_audio)



@router.get('/sample')
def event_details(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return {"title": event.title, "details": event.details}
