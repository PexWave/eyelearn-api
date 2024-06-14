from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from IPython.display import Audio
import time 


import os

# Create your views here.

def getspeech(request):


# download and load all models
    preload_models(
    text_use_small=True,
    coarse_use_small=True,
    fine_use_gpu=False,
    fine_use_small=True,
)

    # generate audio from text
    text_prompt = """
Hi, my name is Vrylle. I am a student of the University of the Philippines. I am currently taking up Bachelor of Science in Computer Science.
    """
    audio_array = generate_audio(text_prompt,history_prompt="v2/en_speaker_2")

    # save audio to disk
    write_wav("C:/Users/NITRO 5/Desktop/wavfiles/bark_generation.wav", SAMPLE_RATE, audio_array)
    
    # play text in notebook
    Audio(audio_array, rate=SAMPLE_RATE)
    
    return HttpResponse("Hello World")


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

def suno_bark():
    
    # Possibly needed if there's a rate limit on calls to Suno Bark

    # Step 1: Text Segmentation
    text = """
    One day, the fox while hunting found a squirrel that was hurt by an accident...
    ... The fox was saved by the squirrel and they became good friends.
    """


    # This is a basic chunking. You might need a more sophisticated approach
    # (e.g., NLP-based) to ensure meaningful segment breaks.
    MAX_CHAR_PER_CHUNK = 200  # You'll need to adjust this based on Suno Bark's actual capacity.
    chunks = chunk_text(text, MAX_CHAR_PER_CHUNK)

    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx + 1}: {chunk}\n")
        

    all_audio_arrays = []

    # Step 2: Audio Conversion
    for idx, chunk in enumerate(chunks):
        audio_array = generate_audio(chunk, history_prompt="v2/en_speaker_2")
        all_audio_arrays.append(audio_array)
        # If there's a rate limit, you might need to wait between API calls:
        time.sleep(2)

        # Step 3a: Saving to Disk (Separate Files)
        file_name = f"C:/Users/NITRO 5/Desktop/wavfiles/chunk_{idx}.wav"
        write_wav(file_name, SAMPLE_RATE, audio_array)

    # Step 3b: Saving to Disk (Single File)
    if all_audio_arrays:
        concatenated_audio = np.concatenate(all_audio_arrays)
        write_wav("C:/Users/NITRO 5/Desktop/wavfiles/full_story.wav", SAMPLE_RATE, concatenated_audio)



def whisper(request):
    
    import whisper

    # Get the absolute path of the file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "wavfiles", "Recording.m4a")
    print(file_path)
    model = whisper.load_model("base.en")
    result = model.transcribe(file_path)
    print(result["text"])

    return HttpResponse(result["text"])


def grammar(request):
    

    corrector = pipeline(
                'text2text-generation',
                'pszemraj/flan-t5-large-grammar-synthesis',
                )
    raw_text = 'i can has cheezburger'
    results = corrector(raw_text)
    print(results)
    return HttpResponse(results)


def comprehension(request):
    
    question_answerer = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')

    context = r"""
    Extractive Question Answering is the task of extracting an answer from a text given a question. An example     of a
    question answering dataset is the SQuAD dataset, which is entirely based on that task. If you would like to fine-tune
    a model on a SQuAD task, you may leverage the examples/pytorch/question-answering/run_squad.py script.
    """

    result = question_answerer(question="What is a good example of a question answering dataset?",     context=context)
    print(f"Answer: '{result['answer']}', score: {round(result['score'], 4)}, start: {result['start']}, end: {result['end']}")

    return HttpResponse(result)



# Django Ninja Functions

@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


class LoginInput(Schema):
    username: str
    password: str

@api.post("/login")
def login(request, user: LoginInput = Form(...)):

    return user





class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


@api.get("/bearer", auth=AuthBearer())
def bearer(request):
    return {"token": request.auth}

