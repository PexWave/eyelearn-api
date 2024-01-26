from ninja.security import HttpBasicAuth, HttpBearer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
import jwt
from django.conf import settings
import datetime
from .models import *
from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from django.contrib.auth.hashers import make_password
from django.forms.models import model_to_dict
from pydantic.fields import ModelField
from typing import Generic, TypeVar
from ninja import Router, Form, Schema
from tempfile import gettempdir
from io import BytesIO
from transformers import pipeline
import asyncio
from faster_whisper import WhisperModel
User = get_user_model()


router = Router()

def retrieve_lessons_helper(level,category,title=None):
    
    if title is None:
        lessons = Lesson.objects.filter(
            level_lessons__level=level.lower(),  # Assuming related_name is 'level_lessons'
            category=category.lower()
        )
    else:
        lessons = Lesson.objects.filter(
            level_lessons__level=level.lower(),  # Assuming related_name is 'level_lessons'
            category=category.lower(),
            title=title.upper()
        ).order_by('item_number')

    lesson_list = []

    print(category)

    for lesson in lessons:
        # For the current lesson, get the associated lyrics
        lesson_lyrics = lesson.lyrics_timestamps.all().order_by('timestamp')
        
        lesson_images = lesson.lesson_images.all().order_by('timestamp')
        # Convert the lyrics to a list of text (or however you want to represent it)
        lyric_data = [{"text": lyric.lyrics, "timestamp": str(lyric.timestamp)} for lyric in lesson_lyrics]
        
        lesson_data = [{"lesson_image": lesson.lesson_images.url, "timestamp": str(lesson.timestamp)} for lesson in lesson_images]
        
        lesson_list.append({
            "id": lesson.id,
            "title": lesson.title,
            "lesson_audio": lesson.lesson_audio.url if lesson.lesson_audio else None,  # Assuming 'lesson_audio' is a FileField
            "bridge_audio": lesson.bridge_audio.url if lesson.bridge_audio else None,  # Assuming 'bridge_audio' is a FileField
            "lesson_image": lesson_data,
            "lesson_lyrics": lyric_data,
            "category": lesson.category,
        })

    print(lesson_list)
    return lesson_list



@router.get('/{level}/{category}/{title}')
def get_lesson(request,level,category,title):
    return retrieve_lessons_helper(level,category,title)

@router.get('/{level}/{category}/')
def get_bundled_lesson(request,level,category):
    return retrieve_lessons_helper(level,category)


@router.post('/confirm/')
def lesson_confirmation(request,recorded_audio: UploadedFile = File(...)):
    
    file_path = BytesIO(recorded_audio.read())
    
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    # pipe = pipeline("automatic-speech-recognition", model="openai/whisper-small", chunk_length_s=30, device=device)
    # prediction = pipe(file_path, batch_size=8)["text"]
    segments, info = model.transcribe(file_path, beam_size=5)


    commands = [
            "yes",
            "no"
            ]

    for segment in segments:
        command = segment.text.lower().strip()
        
        # Search for a command contained within the segment
        print(command)
        for cmd in commands:
            if cmd in command:
                print(cmd)
                return {"command": cmd}

    # If loop completes without returning, then none of the segments contained a command
    return {"command": "none"}      

    