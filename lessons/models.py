from django.db import models


class Lesson(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    lesson_audio = models.FileField(upload_to='lesson_audio/',null=True,blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    bridge_audio = models.FileField(upload_to='bridge_audio/',null=True,blank=True)
    item_number = models.IntegerField(null=True,blank=True)
    
    def __str__(self):
        return self.title
    

class Level(models.Model):
    lessons = models.ManyToManyField('Lesson', null=True, blank=True, related_name='level_lessons')
    level = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.level
    
class Lesson_Image(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="lesson_images")
    lesson_images = models.FileField(upload_to='lesson_images/',null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    
class LyricsTimestamp(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="lyrics_timestamps")
    timestamp = models.CharField(max_length=8)  # This stores a time duration representing the lyric's position in the audio
    lyrics = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.lyrics} - {self.lesson.title}"