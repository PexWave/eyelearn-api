
from ninja import Form, Schema

class PracticeForm(Schema):
  token: str
  practice_id: str
  
  
class ResetPracticeScoreSchema(Schema):
  token: str
  practice_title: str

