
from ninja.security import HttpBasicAuth, HttpBearer
from django.contrib.auth import get_user_model, authenticate
import jwt
from .schema import *
from django.conf import settings
import datetime
from .models import *
from django.db import IntegrityError, transaction
from accounts.models import TokenManager, PupilRecordManager
from practices.models import *
from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from django.contrib.auth.hashers import make_password
from django.forms.models import model_to_dict
from pydantic.fields import ModelField
from django.core.exceptions import ObjectDoesNotExist
from typing import Generic, TypeVar
from ninja import Router, Form, Schema
from django.db import transaction
import numpy as np
import os
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import sys
import subprocess
from tempfile import gettempdir
from io import BytesIO
import asyncio
from faster_whisper import WhisperModel
User = get_user_model()


router = Router()


@router.get('/intonation/')
def get_intonationPractices(request):
    intonation_practices = Practice.objects.filter(
        category="intonation"
    )    
    practice_list = []
    
    for practice in intonation_practices:
        
        practice_lyrics = practice.practice_lyrics_timestamps.all().order_by('timestamp')
        
        practice_images = practice.practice_images.all().order_by('timestamp')
        # Convert the lyrics to a list of text (or however you want to represent it)
        lyric_data = [{"text": lyric.lyrics, "timestamp": str(lyric.timestamp)} for lyric in practice_lyrics]
        
        practice_data = [{"practice_image": practice.practice_images.url, "timestamp": str(practice.timestamp)} for practice in practice_images]
        
      
        practice_list.append({
                            "item_number":practice.item_number,
                            "practice_audio":practice.practice_audio.url,
                            "practice_image": practice_data,
                            "practice_lyrics": lyric_data,
                            "category":practice.category,})
      
    return practice_list


@router.post('/check/')
def check(request,recorded_audio: UploadedFile = File(...)):
    
    file_path = BytesIO(recorded_audio.read())
    
    model = WhisperModel("small.en", device="cpu", compute_type="int8")

    segments, info = model.transcribe(file_path, beam_size=5)

    commands = [
            "practice",
            "grammar", "intonation", "listening comprehension",
            "oral", "vocabulary","noun", "adjective", "spelling",
            "pronoun","adjectives","verb",
            "main menu", "back"
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


@router.post('/intonation/check/')
def intonation_check(request, form: PracticeForm = Form(...), recorded_audio: UploadedFile = File(...)):
    
    file_path = BytesIO(recorded_audio.read())
    
    intonation = Practice.objects.get(category="intonation",item_number=form.item_number)
    
    model = WhisperModel("small.en", device="cuda", compute_type="int8_float16")

    segments, info = model.transcribe(file_path, beam_size=5)

    for segment in segments:
        print(segment.text.lower().strip())
        print(intonation.correct_answer)
        
        if segment.text.lower().strip() == intonation.correct_answer:
            return {"correct":"true"}
        else:
            return {"correct":"false"}
  
  
def retrieve_practices_helper(category,title):
    
    practices = Practice.objects.filter(
        title=title.lower(),  # Assuming related_name is 'level_lessons'
        category=category.lower()
    )

    practice_list = []

    for practice in practices:
        practice_lyrics = practice.practice_lyrics_timestamps.all().order_by('timestamp')
        
        practice_images = practice.practice_images.all().order_by('timestamp')
        # Convert the lyrics to a list of text (or however you want to represent it)
        lyric_data = [{"text": lyric.lyrics, "timestamp": str(lyric.timestamp)} for lyric in practice_lyrics]
        
        practice_data = [{"lesson_image": practice.practice_images.url, "timestamp": str(practice.timestamp)} for practice in practice_images]
        
        practice_list.append({
            "id": practice.id,
            "title": practice.title,
            "choices": practice.choices,
            "lesson_audio": practice.practice_audio.url if practice.practice_audio else None,
            "lesson_image": practice_data,
            "lesson_lyrics": lyric_data,
            "category": practice.category,
        })

    return practice_list      


@router.post('/resetscore/')
def resetScore(request, form: ResetPracticeScoreSchema = Form(...)):
    
    try:
        pupil_record = PupilRecordManager.objects.get(token__jwt_token=form.token, practice=form.practice_title)
        pupil_record.score = 0
        pupil_record.save()
        
    except IntegrityError as e:
        print(e)
        
    

    
    return {"score":pupil_record.score}


@router.get('/{category}/{title}')
def get_practice(request,category,title):
    return retrieve_practices_helper(category,title)



@router.post('/check/pupil/answer')
def check_answer(request, form: PracticeForm = Form(...), recorded_audio: UploadedFile = File(...)):
    
    with transaction.atomic():
        pupil = TokenManager.objects.get(jwt_token=form.token)
        practice = Practice.objects.get(id=form.practice_id)
        pupil_record, created = PupilRecordManager.objects.get_or_create(token=pupil, practice=practice.title)
        model = WhisperModel("small.en", device="cpu", compute_type="int8")

        if practice.title == 'practice-grammar-spelling':
            return check_spelling(form, recorded_audio, model, practice, pupil_record)
        else:
            
            valid_answers = {'a', 'b', 'c', 'd'}
            file_path = BytesIO(recorded_audio.read())
            
            segments, info = model.transcribe(file_path, beam_size=5)

            for segment in segments:    
                form_answer = segment.text.lower().strip().replace(".", "")
                seen_valid_answers = set()
                # Check each word in the answer
                for word in form_answer.split():
                    print(word)
                    if word in valid_answers and word in seen_valid_answers:
                        print("Invalid answer format - Multiple occurrences of the same valid answer")
                        break
                    seen_valid_answers.add(word.replace('.', ''))
                else:
                        # Check if the correct answer is among the seen valid answers
                        if practice.correct_answer.lower() in seen_valid_answers:
                            pupil_record.score += 1
                            pupil_record.save()


                
            return {
                "score":pupil_record.score,
                "answer":form_answer.split()
                    }
                


            
    return {"correct":"false"}

def check_spelling(form, recorded_audio, model, practice, pupil_record):
    file_path = BytesIO(recorded_audio.read())
    
    with transaction.atomic():

        segments, info = model.transcribe(file_path, beam_size=5)

        for segment in segments:
            form_answer = segment.text.lower().strip().replace("-", "")
            # Check each word in the answer
            print(form_answer)

            if form_answer == practice.correct_answer.lower():
                print("Correct!!!!")
                pupil_record.score += 1
                pupil_record.save()
            
            print(pupil_record.score)
        return {
            "score":pupil_record.score,
            "practice_type": "spelling",
            "answer":form_answer.split()
                }
            