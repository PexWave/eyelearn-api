from django.db import models

# Create your models here.

class Practice(models.Model):
    category = models.CharField(max_length=100,null=True,blank=True)
    title = models.CharField(max_length=100,null=True,blank=True)
    item_number = models.IntegerField(null=True,blank=True)
    choices = models.CharField(max_length=100,null=True,blank=True)
    practice_audio = models.FileField(upload_to='practice_audio/',null=True,blank=True)
    correct_answer = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        return f'{self.category} - {self.title}'
    
    class Meta:
        verbose_name_plural = "Practices"
        

class Practice_Image(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name="practice_images")
    practice_images = models.FileField(upload_to='practice_images/',null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    
class PracticeTimestamp(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name="practice_lyrics_timestamps")
    timestamp = models.CharField(max_length=8) # This stores a time duration representing the lyric's position in the audio
    lyrics = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.lyrics} - {self.practice.title}"
    
    
class PracticeQuestionChoice(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name="practice_question_choices")
    choices = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        return f"{self.choices}"