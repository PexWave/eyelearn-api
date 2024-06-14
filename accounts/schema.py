from .models import PupilData, CustomUser
from ninja import ModelSchema, Schema
from datetime import datetime

        
class CreateTeacherSchema(Schema):
    username: str
    email: str
    password: str
    schoolName: str
    
class CreatePupilAccountSchema(Schema):
    nickname: str
    first_name: str
    last_name: str
    age: str
    date_of_birth: str
    gender: str
    profile_pic: str



# SCHEMA FOR SERIALIZERS

class UserAccountSchema(Schema):
    id: int
    first_name: str
    last_name: str
    username: str
    profile_pic: str

class PupilAccountSchema(Schema):
    # date_of_birth: str
    id: int
    gender: str
    age: str
    User: UserAccountSchema = None
    
        

        
