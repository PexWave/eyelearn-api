from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
  
    role = models.CharField(max_length=200,blank=True,null=True)
    profile_pic = models.ImageField(upload_to='profile_pic/',null=True,blank=True)
    school = models.CharField(max_length=200,blank=True,null=True)
    jwt_token = models.TextField(null=True, blank=True,unique=True)
    
    
class TokenManager(models.Model):
    jwt_token = models.TextField(null=True, blank=True,unique=True)
    expiry_date = models.DateTimeField(null=True,blank=True)


class PupilRecordManager(models.Model):
    token = models.ForeignKey(TokenManager,on_delete=models.CASCADE,null=True,blank=True,related_name='pupil_token')
    practice =models.CharField(max_length=200,blank=True,null=True)
    score = models.IntegerField(blank=True,null=True,default=0)

    
class PupilData(models.Model):
    User = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True,related_name='pupil')
    Teacher = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True,related_name='teacher')
    date_of_birth = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=200,blank=True,null=True)
    age = models.CharField(max_length=200,blank=True,null=True)
    level = models.CharField(max_length=200,blank=True,null=True)
    
    def __str__(self):
        return self.User.username
    