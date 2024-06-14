from ninja import Schema

class CreateUserSchema(Schema):
    email: str
    username: str
    repassword: str
    password: str
    first_name: str
    last_name: str
    role: str = None
    
class LoginFormSchema(Schema):
    username: str
    password: str


class CreatePupilSchema(Schema):
    

    username: str
    password: str
    first_name: str
    learners_id_number: str
    gender: str
    age: str
    level: str
    last_name: str
    role: str = "Pupil"