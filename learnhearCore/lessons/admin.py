from django.contrib import admin
from .models import *

# Register your models here.

class LessonAdmin(admin.ModelAdmin):

    search_fields = ('title', 'category')
    
class LyricsAdmin(admin.ModelAdmin):
    
    search_fields = ('lyrics', 'timestamp', 'lesson__title')

admin.site.register(Lesson,LessonAdmin)
admin.site.register(LyricsTimestamp,LyricsAdmin)
admin.site.register(Lesson_Image)
admin.site.register(Level)