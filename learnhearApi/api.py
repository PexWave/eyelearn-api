from ninja.security import HttpBasicAuth
from ninja import Router
from faster_whisper import WhisperModel
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
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import sys
import subprocess
from tempfile import gettempdir
router = Router()

class CustomException(Exception):
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

    def __str__(self):
        return f"{super().__str__()} (Error code: {self.error_code})"


def synthesize_text(text):

    session = boto3.session.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    aws_session_token=settings.AWS_SESSION_TOKEN,
    )

    polly = session.client("polly")

    response = polly.synthesize_speech(
    TextType="ssml",  # Specify text type as SSML
    Text=text,        
     OutputFormat="mp3",
    VoiceId="Brian")


    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(gettempdir(), "speech.mp3")
                try:
                    # Open a file for writing the output as a binary stream
                        with open(output, "wb") as file:
                            file.write(stream.read())
                        
                        return output
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    raise CustomException("Could not write to file, exit gracefully")

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
        



@router.post('/sythesize/')
def synthesize(request, text: str = (...), title: str = (...),word: str = (...),category: str = (...),correct_answer: str = (...),choice: str = (...)):

    if variant == "Practice":
        transcribe_audio_and_timestamp(title, category, output, choice, correct_answer)

    else:
        transcribe_audio_and_timestamp(title, category, output, choice, correct_answer)

    # Play the audio using the platform's default player
    # if sys.platform == "win32":
    #     os.startfile(output)
    # else:
    #     # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
    #     opener = "open" if sys.platform == "darwin" else "xdg-open"
    #     subprocess.call([opener, output])
    return response
    




def transcribe_audio_and_timestamp(title, category, output, choice, correct_answer, variants):
    
    try:
        
        with transaction.atomic():

            content_file = ContentFile(open(output, "rb").read(), name="audio.mp3")

            practice, created = Practice.objects.get_or_create(
                title=title,
                category=category,
                practice_audio=content_file,
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