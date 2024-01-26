from ninja.security import HttpBasicAuth, HttpBearer
from django.contrib.auth import get_user_model
from .schema import CreateTeacherSchema, CreatePupilAccountSchema, PupilAccountSchema
from django.contrib.auth import authenticate
import jwt
from ninja.files import UploadedFile
from django.conf import settings
from datetime import datetime, timedelta
from .forms import *
from .models import *
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.forms.models import model_to_dict
from pydantic.fields import ModelField
from typing import Generic, TypeVar
from django.middleware.csrf import get_token
from ninja.security import django_auth
from django.views.decorators.csrf import csrf_exempt
from ninja import Router, Form, Schema, File
import base64
import imghdr
from django.core.files.base import ContentFile
User = get_user_model()

class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        if User.objects.filter(jwt_token=token).exists():
            
            return token

router = Router(auth=GlobalAuth())

    

# Refresh token
def refresh_token(request, refresh_token: str):
    try:
        # Verify and decode the refresh token
        decoded_token = jwt.decode(refresh_token, secret_key, algorithms=["HS256"])

        # Extract user information from the decoded refresh token
        user_id = decoded_token['user_id']
        username = decoded_token['username']

        # Check if the user exists (you may want to add more error handling)
        user = User.objects.get(id=user_id, usernameS=username)

        # Generate a new access token
        access_token_payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=24)  # New access token expiration
        }
        access_token = jwt.encode(access_token_payload, secret_key, algorithm="HS256")

        return access_token

    except jwt.ExpiredSignatureError:
        return {"detail": "Refresh token has expired."}
    except (jwt.DecodeError, User.DoesNotExist):
        return {"detail": "Invalid refresh token."}
    
# Check if token is expired

def check_token_expiry(token, secret_key):
    try:
        # Decode the token to extract its claims
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Get the expiration time from the claims
        expiration_time = decoded_token.get('exp', None)
        
        if expiration_time is None:
            return False  # Token does not have an expiration time
        
        # Compare the expiration time with the current time
        current_time = datetime.datetime.utcnow()
        return current_time > datetime.datetime.fromtimestamp(expiration_time)
    
    except jwt.ExpiredSignatureError:
        return True  # Token has already expired
    
    except (jwt.DecodeError, jwt.InvalidTokenError):
        return True 


def generate_jwt_token(payload, signing_key):
    return jwt.encode(payload, signing_key, algorithm="HS256")

def generate_and_save_jwt_token():
    # Your payload, customize it according to your needs
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time
    }

    # Get the signing key from Django settings
    JWT_SIGNING_KEY = getattr(settings, "JWT_SIGNING_KEY", None)

    while True:
        try:
            # Try to save the token
            token = TokenManager.objects.create(jwt_token=generate_jwt_token(payload, JWT_SIGNING_KEY))
            break
        except IntegrityError:
            # Handle the case where the token is not unique
            # Regenerate a new token and retry
            continue
        
    
    return token.jwt_token

def get_teacher_jwt_token(request):
    authorization_header = request.headers.get('Authorization')
    token = authorization_header[len('Bearer '):]
    
    user = User.objects.get(jwt_token=token)
    
    return user

def parse_date(date_string):
    """Parses a date string in the format year-month-day.

    Args:
        date_string: A string containing the date in the format year-month-day.

    Returns:
        A datetime object representing the parsed date.
    """
    year, month, day = map(int, date_string.split('-'))
    return datetime(year, month, day)

def get_image_extension(image_data):
    # Use imghdr to determine the image file type
    image_type = imghdr.what(None, image_data)
    
    # Map common image types to file extensions
    extension_mapping = {
        "jpeg": "jpg",
        "png": "png",
        "gif": "gif",
        # Add more as needed
    }

    # Use the mapping or default to None if the type is not recognized
    return extension_mapping.get(image_type, None)


def decode_base64_image(base64_image):
    decoded_image = base64.b64decode(base64_image)
    
    image_name = f"profile_pic.{get_image_extension(decoded_image)}"
    
    return image_name

def serialize(schema_cls, queryset):
     items = [schema_cls.from_orm(i).dict() for i in queryset]
     return items

# FUNCTIONS


# create account for teachers
@router.post('/createAccount')
def create_account(request, form: CreateTeacherSchema = Form(...)):
    
    user = User.objects.create(email=form.email,username=form.username,password=make_password(form.password),school=form.schoolName,role="Teacher")
    
    generate_and_save_jwt_token(user)
    
    return{ 'message': 'Account created successfully'}
    
    
    


# create accounts for pupils
@router.post('/registerPupil') 
def createPupilAccount(request, form: CreatePupilAccountSchema = Form(...)):
   
    teacher = get_teacher_jwt_token(request)
    
    image_name = decode_base64_image(form.profile_pic)
    
    try:
        
        with transaction.atomic():
        
            user = User.objects.create(username=form.nickname,password=make_password("pass1234"),first_name=form.first_name,last_name=form.last_name, profile_pic=ContentFile(base64.b64decode(form.profile_pic), name=image_name), role="Pupil")
            
            pupil = PupilData.objects.create(
                User = user,
                Teacher = teacher,
                gender = form.gender,
                age = form.age,
                date_of_birth = parse_date(form.date_of_birth),
            )
            
            generate_and_save_jwt_token(user)
    
    except IntegrityError as e:
        
        return{ 'message': 'Pupil already exists'}
        
    return{ 'message': 'Pupil created successfully'}
    
   
@router.get('/retrievePupils', response=list[PupilAccountSchema]) 
def retrieve_pupils(request):
    
    teacher = get_teacher_jwt_token(request)

    try:
        pupildata = PupilData.objects.filter(Teacher=teacher)

        print(list(pupildata))
        return list(pupildata)
    except PupilData.DoesNotExist:
        print('No pupil data found for the specified teacher.')
        
        return { 'message': 'No pupil data found for the specified teacher.'}

@router.post('/login', auth=None)
@csrf_exempt
def login(request, form: LoginFormSchema = Form(...)):
    
    user = authenticate(username=form.username, password=form.password)
    
    print(user)
    if user is not None:
    # A backend authenticated the credentials
        login(request,user)
        print(user.is_authenticated)
        if user.role == 'Teacher':
            data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_pic': user.profile_pic.url if user.profile_pic else "",
            'token': user.jwt_token,
            'email': user.email,
            'school': user.school,
            'role': user.role,
            'csrf_token': get_token(request),
            
            }
            
        else:
            pupil_data = PupilData.objects.get(User=user)
            
            data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'teacher': pupil_data.Teacher.first_name + ', ' + pupil_data.Teacher.last_name,
            'profile_pic': user.profile_pic.url,
            'gender': pupil_data.gender,
            'age': pupil_data.age,
            'level': pupil_data.level,
            'token': user.jwt_token,
            'email': user.email,
            'school': user.school,
            'role': user.role,
            }
            
        
        return data
    else:
        # No backend authenticated the credentials
        print('wew')
        return None
   
    # user = User.objects.get(id=1)

    # user_data = model_to_dict(user)
    
    # users = UserSchema(**user_data)
     
    # print(users.dict())
    

@router.post('/upload-profile-pic')
def upload_profile_pic(request, profile_pic: str = Form(...)):
    # user = User.objects.get(jwt_token=token)
    # user.profile_pic = file
    # user.save()

    
    user = get_teacher_jwt_token(request)
    
    image_name = decode_base64_image(profile_pic)
    user.profile_pic.save(image_name, ContentFile(base64.b64decode(profile_pic)), save=True)


    return {"user_profile_pic": user.profile_pic.url}



@router.post('/generateJwtToken', auth=None)
def generateJwtToken(request):
        
    token = generate_and_save_jwt_token()
    
    return { 'token': token}